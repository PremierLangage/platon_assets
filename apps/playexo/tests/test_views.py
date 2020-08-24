import json
import os

from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.test import AsyncClient, Client, TransactionTestCase
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
        self.logged_client = Client()
        self.anon_ac = AsyncClient()
        self.logged_ac = AsyncClient()
        self.user = User.objects.create(username="user", password="password")
        self.logged_ac.force_login(self.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        self.logged_client.force_login(self.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        with open(os.path.join(TEST_DATA_ROOT, "random_add.json")) as f:
            pl_data = json.load(f)
        self.pl = PL.objects.create(name="random_add", data=pl_data)
        self.pl.demo = True
        self.pl.save()
    
    
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
    
    
    async def generic_test_evaluate_random_add(self, client, session):
        response = await database_sync_to_async(client.get)(reverse("playexo:get_pl", args=[self.pl.id]))
        self.assertContains(response, "op1", status_code=200)
        self.assertEquals(await database_sync_to_async(session.objects.count)(), 1)
        context = (await database_sync_to_async(list)(session.objects.all()))[0].context
        result = context["op1"] + context["op2"]
        

        response = await database_sync_to_async(client.post)(reverse("playexo:post_pl"),
                                           {"data": self.pl.data, "name": "random_add"})
        self.assertEquals(await database_sync_to_async(PL.objects.count)(), 2)
        self.assertContains(response, "", status_code=200)
        
        response = await database_sync_to_async(client.post)(reverse("playexo:evaluate_pl", args=[self.pl.id]),
                                     {"answer": result})
        self.assertContains(response, "", status_code=200)
    
    
    async def test_logged_evaluate_random_add(self):
        await self.generic_test_evaluate_random_add(self.logged_client, LoggedPLSession)
    
    
    """
    async def test_anon_evaluate_random_add(self):
        await self.generic_test_evaluate_random_add(self.anon_ac, AnonPLSession)"""
    
    
    async def test_evaluate_no_answer(self):
        response = await self.logged_ac.get(reverse("playexo:get_pl", args=[self.pl.id]))
        self.assertContains(response, "op1", status_code=200)
        self.assertEquals(await database_sync_to_async(LoggedPLSession.objects.count)(), 1)
        response = await self.logged_ac.post(reverse("playexo:evaluate_pl", args=[self.pl.id]))
        self.assertContains(response, "Missing answer field", status_code=400)
    
    
    def test_post(self):
        response = self.logged_client.post(reverse("playexo:post_pl"),
                                           {"data": self.pl.data, "name": "random_add"})
        self.assertEquals(PL.objects.count(), 2)
        self.assertContains(response, "", status_code=200)
