import json
import logging
from typing import AnyStr

from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from assets.models import Asset
from playactivity.models import Activity
from playcourse.models import Course
from playexo.components import components_source
from playexo.exceptions import BuildError, GradeError, SandboxError
from playexo.utils import (DEFAULT_BUILDER, DEFAULT_GRADER, async_get_less_used_sandbox,
                           create_seed,
                           tar_from_dic)


logger = logging.getLogger(__name__)



class PL(Asset):
    """Represents an exercise in the database
    The data field is a jsonfield where the data is shared by all sessions"""
    name = models.CharField(null=False, max_length=100)
    data = models.JSONField(default=dict)
    course = models.ForeignKey(Course, blank=True, null=True, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, blank=True, null=True, on_delete=models.CASCADE)
    demo = models.BooleanField(default=False)
    rerollable = models.BooleanField(default=False)
    compilation_date = models.DateField(default=timezone.now)



class PLSession(models.Model):
    """Represents a session which is unique for a user and a pl (user,pl)"""
    context = models.JSONField(default=dict)  # Built data
    saved_data = models.JSONField(default=dict)  # Answer data
    pl = models.ForeignKey(PL, null=False, on_delete=models.CASCADE)
    seed = models.IntegerField(null=False)
    try_count = models.IntegerField(default=0)
    
    
    @staticmethod
    def _build_env(pl_data: dict, answer: dict = None) -> AnyStr:
        """Creates the environment to execute the builder or the grader
        on the sandbox.
        """
        env = dict(pl_data['__files'])
        env["components.py"] = components_source()
        
        tmp = dict(pl_data)
        del tmp['__files']
        env['pl.json'] = json.dumps(tmp)
        
        if 'grader' in pl_data and 'grader.py' not in env:
            env['grader.py'] = pl_data['grader']
        
        if 'builder' in pl_data and 'builder.py' not in env:
            env['builder.py'] = pl_data['builder']
        
        if answer is not None:
            env['answer.json'] = json.dumps(answer)
        
        return tar_from_dic(env)
    
    
    @classmethod
    async def build_context(cls, pl: PL, seed: int = None, params: dict = None) -> (dict, int):
        """Returns the context built with the pl passed as argument.
        seed and params are optional.
        Returns (context, seed) where context is built using the sandbox and
        seed is the seed used to build the PL. If there was no seed specified,
        it is before calling the builder here.
        It will use a default "config" if there is no "config" field in the PL
        data.
        """
        pl_data = dict(pl.data)
        if params is not None:
            pl_data = pl_data.update(params)
        sandbox = await async_get_less_used_sandbox()
        
        if seed is None and "seed" not in pl_data:
            pl_data["seed"] = create_seed()
        elif seed is not None:
            pl_data["seed"] = seed
        
        env = cls._build_env(pl_data)
        config = pl_data.get("config", {}).get("builder", DEFAULT_BUILDER)
        if config is not None:
            logger.info("Building on sandbox '" + str(sandbox) + "'.")
            try:
                execution = await sandbox.execute(config=config, environment=env)
            except Exception as e:
                raise SandboxError(f"Could not join the sandbox: {e}")
            
            if not execution.success:
                raise BuildError(execution.traceback)
            else:
                response = execution.response
                for command in response["execution"]:
                    if command["exit_code"] != 0:
                        raise BuildError(
                            f"Command: {command['command']}\nstderr: {command['stderr']}")
                return json.loads(response["result"]), pl_data["seed"]
        return pl_data, pl_data["seed"]
    
    
    def get_view_data(self) -> dict:
        """Returns the fields of context useful for the view to display
        the PL"""
        data = {
            "title":      self.context["title"],
            "form":       self.context["form"],
            "text":       self.context["text"],
            "config":     self.context.get("config", {}),
            "rerollable": self.pl.rerollable,
            "demo":       self.pl.demo
        }
        if self.saved_data is not None:
            data["saved"] = self.saved_data
        if "styles" in self.context:
            data["styles"] = self.context["styles"]
        if "scripts" in self.context:
            data["scripts"] = self.context["scripts"],
        return data
    
    
    async def evaluate(self, answers: dict) -> (int, str):
        """Return a tuple (grade, feedback) after evaluating the answer of a
        user.
        The sandbox must be called to evaluate the PL and fields 'grade' and
        'feedback' must be added to the output of the config.
        """
        pl = await database_sync_to_async(self.__getattribute__)("pl")
        sandbox = await async_get_less_used_sandbox()
        context = {**pl.data, **self.context}
        config = context.get("config", {}).get("grader", DEFAULT_GRADER)
        env = self._build_env(context, answer=answers)
        try:
            logger.info("Evaluate on sandbox '" + str(sandbox) + "'.")
            execution = await sandbox.execute(config=config, environment=env)
        except Exception as e:
            raise SandboxError(f"Could not join the sandbox: {e}")
        self.saved_data = answers
        await database_sync_to_async(self.save)()
        
        if not execution.success:
            raise GradeError(execution.traceback)
        else:
            response = execution.response
            for command in response["execution"]:
                if command["exit_code"] != 0:
                    raise GradeError(f"Command: {command['command']}\nstderr: {command['stderr']}")
            new_context = json.loads(response["result"])
        try:
            grade = new_context["grade"]
            feedback = new_context["feedback"]
            del new_context["grade"]
            del new_context["feedback"]
        except KeyError as e:
            raise GradeError("'grade' and 'feedback' fields must be added to context")
        
        self.context.update(new_context)
        self.try_count += 1
        await database_sync_to_async(self.save)()
        
        return grade, feedback
    
    
    async def reroll(self, seed: int = None, params: dict = None):
        """Method used to rebuild a PL with another seed.
        The seed can be specified and fields can be added to the PL using the
        params argument"""
        seed = create_seed() if seed is None else seed
        context, seed = await self.build_context(self.pl, seed, params)
        self.context = context
        self.seed = seed
        self.save()
    
    
    def best_answer(self):
        """Returns the best answer for this session"""
        return Answer.objects.all().select_related("session").filter(session=self).order_by("grade",
                                                                                            "date")
    
    
    def last_answer(self):
        """Retunrs the last answer for this session"""
        return Answer.objects.all().select_related("session").filter(session=self).latest()



class LoggedPLSession(PLSession):
    """PLSession used for a logged user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
    @classmethod
    async def build(cls, pl: PL, user: User, seed: int = None, params: dict = None) -> PLSession:
        context, seed = await super().build_context(pl, seed, params)
        return await database_sync_to_async(cls.objects.create)(context=context, pl=pl, user=user,
                                                                seed=seed)



class AnonPLSession(PLSession):
    """PLSession used for an anonymous user"""
    user_id = models.UUIDField(null=False)
    
    
    @classmethod
    async def build(cls, pl: PL, user_id: str, seed: int = None, params: dict = None) -> PLSession:
        context, seed = await super().build_context(pl, seed, params)
        return await database_sync_to_async(cls.objects.create)(context=context, pl=pl,
                                                                user_id=user_id,
                                                                seed=seed)



class Answer(models.Model):
    """Models used to represents an Answer to a PL in the database"""
    session = models.ForeignKey(PLSession, null=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.now)
    answer = models.JSONField()
    seed = models.IntegerField()
    grade = models.IntegerField(null=False)
