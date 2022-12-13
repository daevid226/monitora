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
    # manufacturer = filters.ModelChoiceFilter(queryset=Actor.objects.all())


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    name = "movies"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(
        detail=True,
        methods=["get"],
        url_name="Get movie info",
        url_path=r"detail",
    )
    def get_movie_detail(self, request, pk=None, *args, **kwargs):
        movie = Movie.objects.get(id=pk)

        data = model_to_dict(movie)
        response = JsonResponse(data)
        response.status_code = status.HTTP_200_OK
        return response
