import datetime
import random

import pytest
from api import models
from django.contrib.auth.models import User
from django.db.models import Max, Min, Q
from faker import Faker
from rest_framework import status
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
class SkipPayTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        # load data
        self.categories = list(models.Category.objects.all().values_list("id", flat=True))
        self.contractors = list(models.Contractor.objects.all().values_list("id", flat=True))
        self.solvers = list(models.Solver.objects.all().values_list("id", flat=True))
        self.issues = {}

        return super().setUp()

    def _new_issue(self):
        return dict(
            name=faker.name(),
            category=random.choice(self.categories),
            contractor=random.choice(self.contractors),
            solver=random.choice(self.solvers),
            status=models.Issue.STATUS_TODO,
            started=faker.date_between(start_date='-30y', end_date='today'),
            description=faker.text(),
        )

    @admin_login
    def test_issue(self):
        for i in range(random.randint(1, 30)):
            issue = self._new_issue()
            response = self.client.post("/issue/", issue, format="json")
            assert response.status_code == 201, response.content

            result = response.json()
            for k, v in issue.items():
                if k == "started":
                    continue
                assert result[k] == v

            self.issues[result["id"]] = result

        # get all
        response = self.client.get("/issue/")
        assert response.status_code == 200, response.content
        assert "results" in response.json()

        # get id
        for issue in self.issues.values():
            issue_id = issue["id"]
            response = self.client.get(f"/issue/{issue_id!s}", {}, True)
            assert response.status_code == 200, response.content
            result = response.json()
            assert result["id"] == issue["id"]

        # test close
        closed_issues = []
        for issue_id in random.choices(list(self.issues.keys()), k=int(len(self.issues) / 2)):
            response = self.client.post(f"/issue/{issue_id!s}/close/", [], format="json")
            assert response.status_code == 202, response.content
            closed_issues.append(response.json())

        # test head
        response = self.client.head(f"/issue/")
        assert response.status_code == 200, response.content
        assert response.content == b""
        assert "shortest-time" in response.headers
        assert "average-time" in response.headers
        assert "longest-time" in response.headers
        
        print(response.headers)

        # check
        for issue in closed_issues:
            issue_id = issue["id"]
            response = self.client.get(f"/issue/{issue_id!s}", {}, True)
            assert response.status_code == 200, response.content
            result = response.json()
            assert result["end"] != None
        
        # TODO: Issue time is end - started
        # endet_times = models.Issue.objects.aggregate(
        #     min_time=Min("end", filter=Q(status=models.Issue.STATUS_DONE, end__isnull=False)),
        #     max_time=Max("end", filter=Q(status=models.Issue.STATUS_DONE, end__isnull=False)),
        # )
        
        # print("ENDS:", endet_times)
        # assert endet_times["min_time"].toordinal() == int(response.headers["shortest-time"])
        # assert endet_times["max_time"].toordinal() == int(response.headers["longest-time"])
        

    @staff_login
    def test_staff(self):
        issue = self._new_issue()
        response = self.client.post("/issue/", issue, format="json")
        assert response.status_code == 403, response.content

        response = self.client.get(f"/issue/")
        assert response.status_code == 200, response.content
