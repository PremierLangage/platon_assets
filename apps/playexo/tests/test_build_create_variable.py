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



class ViewsTestGrosCase(TransactionTestCase):
    
    def setUp(self) -> None:
        super().setUp()
        
        self.sandbox = Sandbox.objects.create(name="test_sandbox",
                                              url=settings.DEFAULT_TEST_SANDBOX,
                                              enabled=True)
        self.anon_ac = AsyncClient()
        self.logged_ac = AsyncClient()
        self.user = User.objects.create(username="user", password="password")
        self.logged_ac.force_login(self.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        
        with open(os.path.join(TEST_DATA_ROOT, "gros.json")) as f:
            pl_data = json.load(f)
            
        # demo = True pour permettre l'usage direct sans activité
        self.pl = PL.objects.create(name="kldjshfqlkjsdfh", data=pl_data, demo=True)

        # test les variables ne sont pas remplacée dans text
        with open(os.path.join(TEST_DATA_ROOT, "variable.json")) as f:
            pl_data = json.load(f)
        self.pl2 = PL.objects.create(name="variable", data=pl_data, demo=True)

    
    def tearDown(self) -> None:
        super().tearDown()
    
    

    

    async def test_logged_build_variable(self):
        response = await self.logged_ac.get(reverse("playexo:get_pl", args=[self.pl2.id]))
        d= json.loads(response.content)
        self.assertEqual(d['title'],"title")
        self.assertEqual(d['text'], "le texte ww{{ var }}ww")
        self.assertIsNotNone(d['vir'])
        self.assertIsNotNone(d['var'])
        self.assertEqual(d['var'],"28")
        self.assertEqual(d['var'], 28)

   # async def test_anon_build_variable(self):
    #    await self.generic_test_build_gros(self.anon_ac, LoggedPLSession, self.pl2, "var")