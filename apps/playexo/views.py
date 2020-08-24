from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound,
                         JsonResponse)

from playexo.models import AnonPLSession, Answer, LoggedPLSession, PL
from playexo.utils import async_is_user_authenticated, get_anonymous_user_id



async def evaluate_pl(request: HttpRequest, pl_id: int) -> HttpResponse:
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    if await async_is_user_authenticated(request.user):
        try:
            session = await database_sync_to_async(LoggedPLSession.objects.get)(user=request.user,
                                                                                pl=pl)
        except LoggedPLSession.DoesNotExist:
            return HttpResponseNotFound("PLSession does not exists")
    elif pl.demo:
        user_id = get_anonymous_user_id(request)
        try:
            session = await database_sync_to_async(AnonPLSession.objects.get)(user_id=user_id,
                                                                              pl=pl)
        except AnonPLSession.DoesNotExist:
            return HttpResponseNotFound("PLSession does not exists")
    else:
        raise PermissionDenied()
    
    if "answer" not in request.POST:
        return HttpResponseBadRequest("Missing answer field")
    answer = request.POST["answer"]
    grade, feedback = await session.evaluate(answer)
    await database_sync_to_async(Answer.objects.create)(session=session, answer=answer, seed=session.seed, grade=grade)
    data = session.get_view_data()
    data["feedback"] = feedback
    data["grade"] = grade
    
    return JsonResponse(data=data)



async def get_pl(request, pl_id: int) -> HttpResponse:
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    if not pl.demo:
        raise PermissionDenied("This PL is not in demo mode")
    
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



def post_pl(request) -> HttpResponse:
    post = request.POST
    if "name" not in post or "data" not in post:
        return HttpResponseBadRequest("Missing 'name' or 'data' field")
    pl = PL.objects.create(name=post["name"], data=post["data"], demo=True)
    return JsonResponse(data={"pl_id": pl.id})



async def reroll(request, pl_id):
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    if not pl.demo or not pl.rerollable:
        raise PermissionDenied("You can't reroll this PL")
    
    if await async_is_user_authenticated(request.user):
        try:
            session = await database_sync_to_async(LoggedPLSession.objects.get)(user=request.user,
                                                                                pl=pl)
        except LoggedPLSession.DoesNotExist:
            return HttpResponseNotFound("PLSession does not exists")
    else:
        user_id = get_anonymous_user_id(request)
        try:
            session = await database_sync_to_async(AnonPLSession.objects.get)(user_id=user_id,
                                                                              pl=pl)
        except AnonPLSession.DoesNotExist:
            return HttpResponseNotFound("PLSession does not exists")
    session.reroll()
    return JsonResponse(session.get_view_data())
