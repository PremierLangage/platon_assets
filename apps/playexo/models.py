from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import BooleanField, CASCADE, DateField, ForeignKey, IntegerField
from django.utils import timezone

from assets.models import Asset
from playcourse.models import Course



class Answer(models.Model):
    session: ForeignKey(PLSession)
    grade: IntegerField(null=False)



class PL(Asset):
    data = JSONField(default={})
    course = ForeignKey(Course, null=True, on_delete=CASCADE)
    demo: BooleanField(default=False)
    rerollable = BooleanField(default=False)
    compilation_data = DateField(default=timezone.now)



class PLSession(models.Model):
    context = JSONField(default={})
    pl: ForeignKey(PL, null=False, on_delete=CASCADE())
    seed: IntegerField(null=False)
    try_count = IntegerField(default=0)
    best_answer = ForeignKey(Answer, null=True)
    last_answer = ForeignKey(Answer, null=True)
    
    
    @classmethod
    def build(cls, seed: int, params: dict):
        return cls.objects.create()
    
    
    def evaluate(self, answers: dict):
        pass
