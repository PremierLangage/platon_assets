from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST



def async_require_post(f):
    async def wrapper(*args, **kwargs):
        return await require_POST(f)(*args, **kwargs)
    return wrapper



def async_require_get(f):
    async def wrapper(*args, **kwargs):
        return await require_GET(f)(*args, **kwargs)
    return wrapper



def async_csrf_exempt(f):
    async def wrapper(*args, **kwargs):
        return await csrf_exempt(f)(*args, **kwargs)
    return wrapper
