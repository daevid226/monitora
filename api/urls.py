from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from monitora import settings
from rest_framework import permissions, routers

from . import views

router = routers.DefaultRouter()
router.register(r"actors", views.ActorViewSet)
router.register(r"movies", views.MovieViewSet)

urlpatterns = [
    path("auth/", include("rest_framework.urls", namespace="api")),
    re_path("search/(?P<search_text>\w+)", views.search, name="api-search"),
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
            re_path(r"swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
            re_path(r"swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
            re_path(r"redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        ]
    )
urlpatterns += router.urls
