import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import AsyncClient, Client, TransactionTestCase
from django.urls import reverse

from django_sandbox.models import Sandbox
from playexo.models import PL


TEST_DATA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")



class ViewsTestCase(TransactionTestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        
        cls.sandbox = Sandbox.objects.create(name="test_sandbox", url=settings.DEFAULT_TEST_SANDBOX,
                                             enabled=True)
    
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
    
    
    async def test_sandbox(self):
        params = {"commands": ["echo test > toto.txt"], "result_path": "toto.txt"}
        result = await self.sandbox.execute(params)
        print(result)
    

    async def test_z(self):
        print("slt")
