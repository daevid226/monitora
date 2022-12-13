from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

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
