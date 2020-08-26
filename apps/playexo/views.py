from typing import Optional

from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound,
                         JsonResponse)
from django.views.decorators.http import require_POST

from playexo.models import AnonPLSession, Answer, LoggedPLSession, PL, PLSession
from playexo.utils import async_is_user_authenticated, get_anonymous_user_id
from utils.decorators import async_require_get, async_require_post



async def retrieve_session(request: HttpRequest, pl: PL) -> Optional[PLSession]:
    """Retrieve the PLSession assiciated to the user for the pl passed as
    argument. If this session does not exists, returns None"""
    if await async_is_user_authenticated(request.user):
        try:
            session = await database_sync_to_async(LoggedPLSession.objects.get)(user=request.user,
                                                                                pl=pl)
        except LoggedPLSession.DoesNotExist:
            return None
    else:
        user_id = get_anonymous_user_id(request)
        try:
            session = await database_sync_to_async(AnonPLSession.objects.get)(user_id=user_id,
                                                                              pl=pl)
        except AnonPLSession.DoesNotExist:
            return None
    return session


@async_require_post
async def evaluate_pl(request: HttpRequest, pl_id: int) -> HttpResponse:
    """View to evaluate a PL that is not in an activity and is in demo mode.
    The post request must have an 'answer' field.
    The session associated to the tuple (user, pl) will evaluate the answer and
    call the grader.
    If the evaluation is successful, it will add an Answer to the database and
    return the new context"""
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    
    if not pl.demo or pl.activity:
        raise PermissionDenied("This PL is not in demo mode or is inside an activity")
    
    session = await retrieve_session(request, pl)
    if session is None:
        return HttpResponseNotFound("Could not retrieve the PL session")
    
    if "answer" not in request.POST:
        return HttpResponseBadRequest("Missing answer field")
    answer = request.POST["answer"]
    
    grade, feedback = await session.evaluate(answer)
    await database_sync_to_async(Answer.objects.create)(session=session, answer=answer,
                                                        seed=session.seed, grade=grade)
    
    data = session.get_view_data()
    data["feedback"] = feedback
    data["grade"] = grade
    
    return JsonResponse(data=data)



@async_require_get
async def get_pl(request, pl_id: int) -> HttpResponse:
    """View to get the data of a PL that is not in an activity and is in
     demo mode.
     The session associated to the tuple (user, pl) will be retrieved,
     and if it does'nt exist, the session will be created and the PL will
     be built by calling the sandbox and executing the builder."""
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    
    if not pl.demo or pl.activity:
        raise PermissionDenied("This PL is not in demo mode or is inside an activity")
    
    if await async_is_user_authenticated(request.user):
        try:
            session = await database_sync_to_async(
                LoggedPLSession.objects.select_related('pl').get)(
                user=request.user, pl=pl)
        except LoggedPLSession.DoesNotExist:
            session = await LoggedPLSession.build(pl, request.user)
    else:
        user_id = get_anonymous_user_id(request)
        try:
            session = await database_sync_to_async(AnonPLSession.objects.select_related('pl').get)(
                user_id=user_id, pl=pl)
        except AnonPLSession.DoesNotExist:
            session = await AnonPLSession.build(pl, user_id)
    return JsonResponse(session.get_view_data())


@require_POST
def post_pl(request) -> HttpResponse:
    """Temporary view to post an already loaded PL easily.
    The post request must have the 'name' and 'data' fields."""
    # TODO to be removed, PL should be created with the loader
    post = request.POST
    if "name" not in post or "data" not in post:
        return HttpResponseBadRequest("Missing 'name' or 'data' field")
    pl = PL.objects.create(name=post["name"], data=post["data"], demo=True)
    return JsonResponse(data={"pl_id": pl.id})


@async_require_post
async def reroll(request, pl_id):
    """View to get the data of a PL that is not in an activity and is in
     demo mode.
     The session associated to the tuple (user, pl) will be retrieved, and the
     context will be rebuilt by calling the sandbox and executing the builder.
     A 'seed' field is optional to reroll the PL."""
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    
    if not pl.demo or pl.activity:
        raise PermissionDenied("This PL is not in demo mode or is inside an activity")
    
    session = await retrieve_session(request, pl)
    if session is None:
        return HttpResponseNotFound("Could not retrieve the PL session")
    if "seed" in request.POST:
        await session.reroll(seed=request.POST["seed"])
    else:
        await session.reroll()
    
    return JsonResponse(session.get_view_data())


@async_require_post
async def save_answer(request, pl_id):
    """View to save the data of a user : the answer fields.
    The field  will be sent with the pl data when the PL will be retrieved, so
    the user can get back to the state his exercise was when he left."""
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    
    if not pl.demo or pl.activity:
        raise PermissionDenied("This PL is not in demo mode or is inside an activity")
    
    session = await retrieve_session(request, pl)
    if session is None:
        return HttpResponseNotFound("Could not retrieve the PL session")
    
    if "answer" not in request.POST:
        return HttpResponseBadRequest("Missing answer field")
    session.saved_data = request.POST["answer"]
    database_sync_to_async(session.save)()
    
    return JsonResponse(session.get_view_data())
