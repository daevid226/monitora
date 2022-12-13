from django.urls import include, path, re_path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"actors", views.ActorViewSet)
router.register(r"movies", views.MovieViewSet)

urlpatterns = [
    path("auth/", include("rest_framework.urls", namespace="api")),
    re_path("search/(?P<search_text>\w+)", views.search, name="api-search"),
]

urlpatterns += router.urls
