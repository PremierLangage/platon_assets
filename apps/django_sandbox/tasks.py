import logging

from aiohttp import ClientError
from asgiref.sync import async_to_sync
from celery import shared_task

from django_sandbox.models import Sandbox


logger = logging.getLogger(__name__)



@shared_task
def poll_usage(sandbox_pk: int) -> None:
    sandbox = Sandbox.objects.get(pk=sandbox_pk)
    async_to_sync(sandbox.poll_usage)()



@shared_task
def poll_specifications(sandbox_pk: int) -> None:
    sandbox = Sandbox.objects.get(pk=sandbox_pk)
    try:
        if sandbox.enabled:
            async_to_sync(sandbox.poll_specifications)()
    except ClientError:
        logger.info(f"Could not join Sandbox ({sandbox})")
