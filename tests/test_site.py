import bs4
import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase, LiveServerTestCase

from monitora import views

import os
os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:80'
    


@pytest.mark.django_db
class _TestCsrf(TestCase):
    
    def setUp(self):
        self.admin = User.objects.get(username="admin")
    
    def _test_csrf_protected(self):
        client = RequestFactory()
        request = client.post("/index/")
        response = views.Index().post(request)
        self.assertEqual(response.status_code, 403, response.content)


@pytest.mark.django_db
class TestIndex(LiveServerTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        # self.admin = admin = User.objects.get(username="admin")
        # if not admin:
        self.admin = User.objects.create_user(username="admin", password="admin")
        self.client.force_login(self.admin)
    
    def tearDown(self):
        self.client.logout()

    def test_index(self):
        response = self.client.get("/index/")
        self.assertEqual(response.status_code, 200, msg=response.content)

    def test_search(self):
        search_text = "ab"
        
        response = self.client.post("/index/", {"search_text": search_text})
        self.assertEqual(response.status_code, 200, msg=response.content)

        # parse and check movies
        soup = bs4.BeautifulSoup(response.content, "lxml")

        # find movies and actors
        movie_list_node = soup.find("body").find("div", {"class": "movie-lisr"})
        self.assertIsNotNone(movie_list_node)

        actor_list_node = soup.find("body").find("div", {"class": "actor-lisr"})
        self.assertIsNotNone(actor_list_node)
