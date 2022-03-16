from rest_framework import serializers

from movienight_auth.models import User
from movies.models import Movie, MovieNight, MovieNightInvitation, Genre


class GenreField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(name=data)[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["title", "year", "runtime_minutes", "imdb_id", "genres", "plot", "is_full_record"]
        read_only_fields = ["title", "year", "runtime_minutes", "imdb_id", "genres", "plot", "is_full_record"]

class MovieTitleAndUrlSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField("movie-detail", read_only=True)

    class Meta:
        model = Movie
        fields = ["title", "url"]


class MovieNightInvitationSerializer(serializers.ModelSerializer):
    invitee = serializers.HyperlinkedRelatedField(
        "user-detail", read_only=True, lookup_field="email"
    )

    class Meta:
        model = MovieNightInvitation
        fields = "__all__"
        read_only_fields = ["attendance_confirmed", "movie_night", "invitee"]


class MovieNightInvitationCreationSerializer(serializers.ModelSerializer):
    invitee = serializers.HyperlinkedRelatedField(
        "user-detail", queryset=User.objects.all(), lookup_field="email"
    )

    class Meta:
        model = MovieNightInvitation
        fields = ["invitee"]

    def __init__(self, movie_night, *args, **kwargs):
        self.movie_night = movie_night
        super(MovieNightInvitationCreationSerializer, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        kwargs["movie_night"] = self.movie_night
        return super(MovieNightInvitationCreationSerializer, self).save(**kwargs)

    def validate_invitee(self, invitee):
        existing_invitation = MovieNightInvitation.objects.filter(
            invitee=invitee, movie_night=self.movie_night
        ).first()
        if existing_invitation:
            raise serializers.ValidationError(
                f"{invitee.email} has already been invited to this Movie Night"
            )
        return invitee


class MovieNightSerializer(serializers.ModelSerializer):
    movie = MovieTitleAndUrlSerializer(read_only=True)
    creator = serializers.HyperlinkedRelatedField(
        "user-detail", read_only=True, lookup_field="email"
    )
    invites = MovieNightInvitationSerializer(read_only=True, many=True)

    class Meta:
        model = MovieNight
        fields = "__all__"
        read_only_fields = ["movie", "creator", "start_notification_sent", "invites"]


class MovieNightCreateSerializer(MovieNightSerializer):
    movie = serializers.HyperlinkedRelatedField(
        view_name="movie-detail", queryset=Movie.objects.all()
    )

    class Meta(MovieNightSerializer.Meta):
        read_only_fields = ["start_notification_sent", "invites"]


class MovieSearchSerializer(serializers.Serializer):
    term = serializers.CharField()
