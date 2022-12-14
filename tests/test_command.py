import pytest
from django.core.management import call_command


@pytest.mark.django_db(transaction=True)
def test_dump_movies(django_db_blocker):
    with django_db_blocker.unblock():
        call_command("dumpmovies --clear-database")