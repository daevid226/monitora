from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import settings, views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("login/", views.Login.as_view(), name="login"),
    re_path(r"^$", RedirectView.as_view(url="/index/")),
    re_path("^index/movie/(?P<movie_id>\d+)", views.MovieDetail.as_view(), name="movie-detail"),
    re_path("^index/actor/(?P<actor_id>\d+)", views.ActorDetail.as_view(), name="actor-detail"),
    re_path("^index/", views.Index.as_view(), name="index"),
]

if settings.SWAGGE_UI:
    schema_view = get_schema_view(
        openapi.Info(
            title="Monitora API",
            default_version="v1",
            description="Monitora Demo",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="daevid226@google.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=[permissions.IsAuthenticated],
    )

    urlpatterns.extend(
        [
            re_path(
                r"^api/swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"
            ),
            re_path(r"^api/swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
            re_path(r"^api/redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        ]
    )
