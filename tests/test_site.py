import pytest
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
import bs4

from monitora import views

@pytest.mark.django_db
class TestIndex(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.admin = User.objects.get(username="admin")
        self.client.force_login(self.admin)

    def tearDown(self):
        self.client.logout()

    def test_index(self):
        response = self.client.get("/index/")
        self.assertEqual(response.status_code, 200, msg=response.content)

    def test_csrf_protected(self):
        client = Client()
        client.force_login(self.admin)
        request = client.post('/index/', {})
        response = views.Index().post(request)
        self.assertEqual(response.status_code, 403)
        
    def test_search(self):
        search_text = "ab"
        response = self.client.post("/index/", {"search_text": search_text}, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200, msg=response.content)
        
        # parse and check movies
        soup = bs4.BeautifulSoup(response.text, "lxml")
        
        # find movies and actors
        movie_list_node = soup.find("body").find("div", {"class": "movie-lisr"})
        self.assertIsNotNone(movie_list_node)
        
        actor_list_node = soup.find("body").find("div", {"class": "actor-lisr"})
        self.assertIsNotNone(movie_list_node)