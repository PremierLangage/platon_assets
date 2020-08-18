import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import AsyncClient, Client, TestCase, TransactionTestCase
from django.urls import reverse

from django_sandbox.models import Sandbox
from playexo.models import PL


TEST_DATA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")



class ViewsTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        
        cls.sandbox = Sandbox.objects.create(name="test_sandbox", url=settings.DEFAULT_TEST_SANDBOX,
                                             enabled=True)
        
        cls.user = User.objects.create_user(username='user', password='12345')
        cls.c = AsyncClient()
        cls.c.force_login(cls.user, backend=settings.AUTHENTICATION_BACKENDS[0])
        
        with open(os.path.join(TEST_DATA_ROOT, "random_add.json")) as json_file:
            pl_data = json.load(json_file)
        cls.pl = PL.objects.create(name="random_add", data=pl_data)
    
    
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
    
    """
    async def test_build_pl(self):
        print(self.pl.name)
        response = await self.c.get(reverse("playexo:get_pl", args=[self.pl.id]))
        print(response.content)
        self.assertContains(response, "op1", status_code=200)
        """
