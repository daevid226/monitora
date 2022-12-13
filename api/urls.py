from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"actors", views.ActorViewSet)
router.register(r"movies", views.MovieViewSet)

urlpatterns = [
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]

urlpatterns += router.urls
