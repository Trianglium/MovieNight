from django.shortcuts import redirect
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from movies.api.serializers import (
    MovieSerializer,
    MovieNightSerializer,
    MovieNightInvitationSerializer,
    GenreSerializer,
    MovieSearchSerializer,
    MovieNightInvitationCreationSerializer,
    MovieNightCreateSerializer,
)
from movies.models import Movie, MovieNight, MovieNightInvitation, Genre
from movies.omdb_integration import fill_movie_details, search_and_save


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    @action(methods=["get"], detail=False)
    def search(self, request):
        search_serializer = MovieSearchSerializer(data=request.GET)

        if not search_serializer.is_valid():
            return Response(search_serializer.errors)

        term = search_serializer.data["term"]

        search_and_save(term)

        movies = self.get_queryset().filter(title__icontains=term)

        page = self.paginate_queryset(movies)

        if page is not None:
            serializer = MovieSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        return Response(
            MovieSerializer(movies, many=True, context={"request": request}).data
        )


class MovieNightViewSet(viewsets.ModelViewSet):
    queryset = MovieNight.objects.all()

    def get_object(self):
        movie_night = super(MovieNightViewSet, self).get_object()
        if (
            movie_night.creator != self.request.user
            and movie_night.invites.filter(invitee=self.request.user).count() == 0
        ):
            raise PermissionDenied()
        return movie_night

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(creator=self.request.user)
        return super(MovieNightViewSet, self).get_queryset()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=False)
    def invited(self, request):
        movie_nights = MovieNight.objects.filter(
            invites__in=MovieNightInvitation.objects.filter(invitee=request.user)
        )

        page = self.paginate_queryset(movie_nights)

        if page is not None:
            serializer = MovieNightSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        return Response(
            MovieNightSerializer(
                movie_nights, many=True, context={"request": request}
            ).data
        )

    @action(methods=["post"], detail=True)
    def invite(self, request, pk):
        movie_night = self.get_object()
        if movie_night.creator != self.request.user:
            raise PermissionDenied()

        serializer = MovieNightInvitationCreationSerializer(
            movie_night, data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors)

        serializer.save()
        return redirect("movienight-detail", (movie_night.pk,))


class MovieNightInvitationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MovieNightInvitationSerializer

    def get_queryset(self):
        return MovieNightInvitation.objects.filter(invitee=self.request.user)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
