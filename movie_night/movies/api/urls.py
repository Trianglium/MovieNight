from django.urls import include, path
from rest_framework.routers import DefaultRouter

from movies.api.views import (
    MovieViewSet,
    MovieNightViewSet,
    MovieNightInvitationViewSet,
    GenreViewSet,
)

router = DefaultRouter()
router.register("movies", MovieViewSet)
router.register("movie-nights", MovieNightViewSet, basename="movienight")
router.register(
    "movie-night-invitations",
    MovieNightInvitationViewSet,
    basename="movienightinvitation",
)
router.register("genres", GenreViewSet)

urlpatterns = [path("", include(router.urls))]
