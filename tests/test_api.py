import random

import pytest
from api import models
from django.contrib.auth.models import User
from faker import Faker
from rest_framework.test import APIClient, APITestCase

# Generator fake data
faker = Faker()


def _login_helper(fn, username, password):
    def _fn(*args, **kwargs):
        _self = args[0]

        user = User.objects.all().filter(username=username)
        _self.client.force_login(user[0])
        try:
            return fn(*args, **kwargs)
        finally:
            _self.client.logout()

    return _fn


def admin_login(fn):
    return _login_helper(fn, "admin", "admin")


def staff_login(fn):
    return _login_helper(fn, "staff", "staff")


@pytest.mark.django_db(transaction=True)
class ApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        # load data
        self.actors = list(models.Actor.objects.all().values_list("id", flat=True))
        self.movies = list(models.Movies.objects.all().values_list("id", flat=True))

        return super().setUp()

    def _new_actor(self):
        fullName = faker.name()
        givenName, surname = fullName.split(" ")
        return dict(
            fullName=fullName,
            givenName=givenName,
            lastName=surname,
            url="",
        )

    def _new_movie(self):
        pass
    
    @admin_login
    def test_post_actor(self):
        pass
    
    @admin_login
    def test_post_movie(self):
        pass
    
    @admin_login
    def test_get_actors(self):
        response = self.client.get("/api/actors/", format="json")
        assert response.status_code == 200, response.content
        result = response.json()
        actors = result["results"]
        
        #for actor in random.choice(actors, )
        

    @staff_login
    def test_get_movies(self):
        pass

    @staff_login
    def test_search(self):
        pass
    
    @staff_login
    def test_staff(self):
        actor = self._new_actor()
        response = self.client.post("/api/actors/", actor, format="json")
        assert response.status_code == 403, response.content

        response = self.client.get(f"/api/movies/")
        assert response.status_code == 200, response.content
