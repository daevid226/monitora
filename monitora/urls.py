from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls"), name="api"),
    path("login/", views.Login.as_view(), name="login"),
    re_path(r"^$", RedirectView.as_view(url="/index/")),
    re_path("^index/movie/(?P<movie_id>\d+)", views.MovieDetail.as_view(), name="movie-detail"),
    re_path("^index/actor/(?P<actor_id>\d+)", views.ActorDetail.as_view(), name="actor-detail"),
    re_path("^index/", views.Index.as_view(), name="index"),
]
