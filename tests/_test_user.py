import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_staff_user():
    staff = User.objects.get(username="staff")
    assert not staff.is_superuser
    assert staff.is_staff


@pytest.mark.django_db
def test_admin_user():
    admin = User.objects.get(username="admin")
    assert admin.is_superuser


@pytest.mark.django_db
def test_staff_login(client):
    client.login(username="staff", password="staff")
    client.logout()


@pytest.mark.django_db(transaction=True)
def test_add_user(client):
    username = "daevid226"
    password = "asdf1234&*&^"
    new_user = User.objects.create_user(username=username, password=password)
    user = User.objects.get(username="daevid226")

    assert new_user == user

    client.force_login(user)

    response = client.get("/users")
    assert response.status_code == 301

    client.logout()
