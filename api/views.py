from functools import partial

import unidecode
from django.db import connection
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes

from .models import Actor, Movie
from .serializers import ActorSerializer, MovieSerializer

# from django_filters.rest_framework import FilterSet, filters


class ActorViewSet(viewsets.ModelViewSet):
    template_name = "profile_detail.html"

    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    name = "actors"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    name = "movies"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def search(request, search_text):
    """
    Fulltext search
    """
    search_text = unidecode.unidecode(search_text)

    if connection.vendor == "sqlite":
        movie_filter = dict(title__contains=search_text)
        actor_filter = dict(fullName__contains=search_text)
    else:
        movie_filter = dict(title__contains=search_text)
        actor_filter = dict(fullName__contains=search_text)

    movies = Movie.objects.filter(**movie_filter).only("id", "title", "url")
    actors = Actor.objects.filter(**actor_filter).only("id", "fullName", "url")

    data = {
        "results": {
            "movies": list(map(partial(model_to_dict, fields=["id", "title", "url"]), movies)),
            "actors": list(map(partial(model_to_dict, fields=["id", "fullName", "url"]), actors)),
        }
    }

    response = JsonResponse(data)
    response.status_code = status.HTTP_200_OK
    return response
