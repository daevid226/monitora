import random

import pytest
from api import models
from django.contrib.auth.models import User
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

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
        super().setUp()

        # load data
        self.actors = list(models.Actor.objects.all())
        self.movies = list(models.Movie.objects.all())  # .values_list("id", flat=True))

    def _new_actor(self):
        fullName = faker.name()
        givenName, surname = fullName.split(" ")
        return dict(
            fullName=fullName,
            givenName=givenName,
            lastName=surname,
            url="/api/actors/",
        )

    def _new_movie(self):
        return dict(
            title=faker.name(),
            url="/api/movies/",
            actors=[actor.id for actor in random.choices(self.actors, k=4)],
        )

    @staff_login
    def test_get_actors(self):
        response = self.client.get("/api/actors/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)
        result = response.json()
        actors = result["results"]

        for actor in random.choices(actors, k=14):
            response = self.client.get(f"/api/actors/{actor['id']}", {}, True, format="json")
            self.assertEqual(response.status_code, 200, msg=response.content)
            self.assertEqual(actor["id"], response.json()["id"])

    @staff_login
    def test_get_movies(self):
        response = self.client.get("/api/movies/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)
        result = response.json()
        movies = result["results"]

        for movie in random.choices(movies, k=14):
            response = self.client.get(f"/api/movies/{movie['id']}", {}, True)
            self.assertEqual(response.status_code, 200, msg=response.content)
            result = response.json()
            self.assertEqual(movie["id"], result["id"])
            self.assertTrue(len(result["actors"]) > 0)

    @admin_login
    def test_crud_actor(self):
        actor = self._new_actor()
        response = self.client.post("/api/actors/", actor, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.content)

        result = response.json()
        actor_id = result["id"]

        # check in database
        model_actor = models.Actor.objects.get(pk=actor_id)
        self.assertIsInstance(model_actor, models.Actor)

        # get
        response = self.client.get(f"/api/actors/{actor_id}", {}, True, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)
        self.assertEqual(response.json()["id"], actor_id)

        # delete
        response = self.client.delete(f"/api/actors/{actor_id}", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)

    @admin_login
    def test_crud_movie(self):
        movie = self._new_movie()
        response = self.client.post("/api/movies/", movie, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=response.content)

        result = response.json()
        response = self.client.get(f"/api/movies/{result['id']}", {}, True, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)

        # delete
        response = self.client.delete(f"/api/movies/{result['id']}", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)

    @staff_login
    def test_search(self):
        search_text = "ab"

        response = self.client.get("/api/search/" + search_text, {}, True)
        self.assertEqual(response.status_code, 200, msg=response.content)

        result = response.json()["results"]
        movies, actors = result.get("movies"), result.get("actors")
        self.assertTrue(movies)
        self.assertTrue(actors)

        self.assertEqual(len(movies), 4)
        self.assertEqual(len(actors), 10)
