import pytest
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestIndex(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        admin = User.objects.get(username="admin")
        self.client.force_login(admin)

    def tearDown(self):
        self.client.logout()

    def test_index(self):
        response = self.client.get("/index/")
        self.assertEqual(response.status_code, 200, msg=response.content)

    def test_search(self):
        search_text = "ab"
        response = self.client.post("/index/", {"search_text": search_text}, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200, msg=response.content)