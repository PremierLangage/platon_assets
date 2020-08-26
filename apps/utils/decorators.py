import asyncio
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST



def async_require_post(f):
    async def wrapper(*args, **kwargs):
        res = require_POST(f)(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return await res
        return res
    return wrapper



def async_require_get(f):
    async def wrapper(*args, **kwargs):
        res = require_GET(f)(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return await res
        return res
    return wrapper



def async_csrf_exempt(f):
    async def wrapper(*args, **kwargs):
        res = csrf_exempt(f)(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return await res
        return res
    return wrapper
