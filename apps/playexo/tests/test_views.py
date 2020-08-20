import json
import os

from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.test import AsyncClient, TransactionTestCase
from django.urls import reverse

from django_sandbox.models import Sandbox
from playexo.models import AnonPLSession, LoggedPLSession, PL


TEST_DATA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")



class ViewsTestCase(TransactionTestCase):
    
    def setUp(self) -> None:
        super().setUp()
        
        self.sandbox = Sandbox.objects.create(name="test_sandbox",
                                              url=settings.DEFAULT_TEST_SANDBOX,
                                              enabled=True)
        self.anon_ac = AsyncClient()
        self.logged_ac = AsyncClient()
        self.user = User.objects.create(username="user", password="password")
        self.logged_ac.force_login(self.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        
        with open(os.path.join(TEST_DATA_ROOT, "random_add.json")) as f:
            pl_data = json.load(f)
        self.pl = PL.objects.create(name="random_add", data=pl_data)
    
    
    def tearDown(self) -> None:
        super().tearDown()
    
    
    async def test_sandbox(self):
        params = {"commands": ["echo test > toto.txt"], "result_path": "toto.txt"}
        result = await self.sandbox.execute(params)
        self.assertEquals(result.response["result"], "test\n")
    
    
    async def generic_test_build_random_add(self, client, session):
        self.assertEquals(await database_sync_to_async(session.objects.count)(), 0)
        response = await client.get(reverse("playexo:get_pl", args=[self.pl.id]))
        self.assertEquals(await database_sync_to_async(session.objects.count)(), 1)
        self.assertContains(response, "op1", status_code=200)
        response = await client.get(reverse("playexo:get_pl", args=[self.pl.id]))
        self.assertEquals(await database_sync_to_async(session.objects.count)(), 1)
        self.assertContains(response, "op1", status_code=200)
    
    
    async def test_logged_build_random_add(self):
        await self.generic_test_build_random_add(self.logged_ac, LoggedPLSession)
    
    
    async def test_anon_build_random_add(self):
        await self.generic_test_build_random_add(self.anon_ac, AnonPLSession)
