from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound,
                         JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from playexo.models import AnonPLSession, LoggedPLSession, PL
from playexo.utils import async_is_user_authenticated, get_anonymous_user_id


@require_POST
async def evaluate_pl(request: HttpRequest, pl_id: int) -> HttpResponse:
    answer = request.POST["answer"]
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    if request.user:
        try:
            session = await database_sync_to_async(LoggedPLSession.objects.get)(user=request.user, pl=pl)
        except LoggedPLSession.DoesNotExist:
            return HttpResponseNotFound("PLSession does not exists")
    else:
        user_id = get_anonymous_user_id(request)
        try:
            session = await database_sync_to_async(AnonPLSession.objects.get)(user_id=user_id, pl=pl)
        except AnonPLSession.DoesNotExist:
            return HttpResponseNotFound("PLSession does not exists")
    
    grade, feedback = session.evaluate(answer)
    
    data = session.get_view_data()
    data["feedback"] = feedback
    data["grade"] = grade
    return JsonResponse(data=data)


async def get_pl(request, pl_id: int) -> HttpResponse:
    try:
        pl = await database_sync_to_async(PL.objects.get)(id=pl_id)
    except PL.DoesNotExist:
        return HttpResponseNotFound("PL does not exists")
    if await async_is_user_authenticated(request.user):
        try:
            session = await database_sync_to_async(LoggedPLSession.objects.select_related('pl').get)(
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



@csrf_exempt
@require_POST
def post_pl(request) -> HttpResponse:
    post = request.POST
    if "name" not in post or "data" not in post:
        return HttpResponseBadRequest("Missing 'name' or 'data' field")
    name = request.POST["name"]
    data = request.POST["data"]
    pl = PL.objects.create(name=name, data=data)
    return JsonResponse(data={"pl_id": pl.id})
