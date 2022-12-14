from django.contrib import admin  # noqa

from .models import Actor, Movie, MovieActor


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fullName",
        "givenName",
        "lastName",
        "url",
    )
    list_per_page = 25


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "url",
    )
    list_per_page = 25


@admin.register(MovieActor)
class MovieActorAdmin(admin.ModelAdmin):
    list_display = (
        "movie",
        "actor",
    )
    list_per_page = 25
