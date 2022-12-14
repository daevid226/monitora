import os

import pytest
from django.conf import settings
from django.contrib.auth.models import ContentType, Permission, User
from django.core.management import call_command
from django.test import Client


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    settings.DATABASES["default"] = {
        "ATOMIC_REQUESTS": False,
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory",
    }

    # clear database & migrate & add users
    with django_db_blocker.unblock():
        call_command("sqlflush")
        call_command("migrate")

        # load data
        call_command("loaddata", os.path.join(settings.BASE_DIR, "tests", "initial_test_data.json"))

        # insert users
        User.objects.all().delete()

        # create users
        User.objects.create_superuser(
            username="admin",
            email="admin@monitora.cz",
            password="admin",
        )

        #
        staff_user = User.objects.create(
            username="staff",
            email="staff@monitora.cz",
            password="staff",
            is_staff=True,
        )

        permission_content_types = ContentType.objects.all().filter(app_label="api").values_list("id", flat=True)

        staff_permissions = (
            Permission.objects.all()
            .filter(codename__icontains="view")
            .filter(content_type_id__in=permission_content_types)
        )

        for perm in staff_permissions:
            staff_user.user_permissions.add(perm)


@pytest.mark.usefixtures("django_db_setup", scope="module")
@pytest.fixture(scope="module")
def client():
    return Client()
