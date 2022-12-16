import bs4
import pytest
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase
from monitora import views


@pytest.mark.django_db
class TestIndex(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.admin = User.objects.get(username="admin")
        self.client.force_login(self.admin)

        print(django_settings)
        session = self.client.session

        # # Update session's cookie
        session_cookie_name = django_settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie_name] = session.session_key

    def tearDown(self):
        self.client.logout()

    def test_index(self):
        response = self.client.get("/index/")
        self.assertEqual(response.status_code, 200, msg=response.content)

    def _test_csrf_protected(self):
        client = RequestFactory()
        client.force_login(self.admin)
        request = client.post("/index/")
        response = views.Index().post(request)
        self.assertEqual(response.status_code, 403, response.content)

    def test_search(self):
        search_text = "ab"
        response = self.client.post("/index/", {"search_text": search_text})
        self.assertEqual(response.status_code, 200, msg=response.content)

        # parse and check movies
        soup = bs4.BeautifulSoup(response.content, "lxml")

        print(response.content)

        # find movies and actors
        movie_list_node = soup.find("body").find("div", {"class": "movie-lisr"})
        self.assertIsNotNone(movie_list_node)

        actor_list_node = soup.find("body").find("div", {"class": "actor-lisr"})
        self.assertIsNotNone(movie_list_node)
