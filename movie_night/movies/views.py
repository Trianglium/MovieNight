from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from movies.forms import SearchForm, MovieNightForm, InviteeForm, AttendanceForm
from movies.models import Movie, MovieNight, MovieNightInvitation
from movies.omdb_integration import search_and_save, fill_movie_details


def index(request):
    return render(request, "movies/index.html")


@login_required
def movie_search(request):
    search_form = SearchForm(request.POST)

    if search_form.is_valid() and search_form.cleaned_data["term"]:
        term = search_form.cleaned_data["term"]
        search_and_save(term)
        movie_list = Movie.objects.filter(title__icontains=term)
        did_search = True
    else:
        movie_list = []
        did_search = False

    return render(
        request,
        "movies/search.html",
        {
            "page_group": "search",
            "search_form": search_form,
            "movie_list": movie_list,
            "did_search": did_search,
        },
    )


@login_required
def movie_night_list(request):
    start_time_after = timezone.now() - timedelta(hours=2)
    created_movie_nights = MovieNight.objects.filter(
        creator=request.user, start_time__gt=start_time_after
    )
    invited_movie_nights = MovieNight.objects.filter(
        start_time__gt=start_time_after,
        invites__in=MovieNightInvitation.objects.filter(invitee=request.user),
    )

    return render(
        request,
        "movies/movie_night_list.html",
        {
            "page_group": "movie-nights",
            "created_movie_nights": created_movie_nights,
            "invited_movie_nights": invited_movie_nights,
        },
    )


@login_required
def movie_detail(request, imdb_id):
    movie = get_object_or_404(Movie, imdb_id=imdb_id)
    fill_movie_details(movie)
    if request.method == "POST":
        movie_night_form = MovieNightForm(request.POST)
        if movie_night_form.is_valid():
            movie_night = movie_night_form.save(False)
            movie_night.movie = movie
            movie_night.creator = request.user
            movie_night.save()
            return redirect("movie_night_detail_ui", movie_night.pk)
    else:
        movie_night_form = MovieNightForm()
    return render(
        request,
        "movies/movie_detail.html",
        {"page_group": "search", "movie": movie, "movie_night_form": movie_night_form},
    )


@login_required
def movie_night_detail(request, pk):
    movie_night = get_object_or_404(MovieNight, pk=pk)

    is_creator = movie_night.creator == request.user

    invitee_form = None
    attendance_form = None

    invitees = {invitation.invitee for invitation in movie_night.invites.all()}

    is_in_the_past = movie_night.start_time < timezone.now()

    if not is_creator:
        if request.user not in invitees:
            raise PermissionDenied("You do not have access to this MovieNight")

        invitation = movie_night.invites.filter(invitee=request.user).first()

        if not is_in_the_past and request.method == "POST":
            attendance_form = AttendanceForm(request.POST, instance=invitation)
            if attendance_form.is_valid():
                attendance_form.save()
        else:
            attendance_form = AttendanceForm(instance=invitation)
    else:
        if not is_in_the_past and request.method == "POST":
            invitee_form = InviteeForm(request.POST)

            if invitee_form.is_valid():
                invitee = invitee_form._user

                if invitee == request.user or invitee in invitees:
                    invitee_form.add_error(
                        "email", "That user is the creator or already invited"
                    )
                else:
                    MovieNightInvitation.objects.create(
                        invitee=invitee, movie_night=movie_night
                    )
                    return redirect(request.path)  # effectively, just reload the page
        else:
            invitee_form = InviteeForm()

    return render(
        request,
        "movies/movie_night_detail.html",
        {
            "page_group": "movie-nights",
            "movie_night": movie_night,
            "is_creator": is_creator,
            "invitee_form": invitee_form,
            "attendance_form": attendance_form,
            "is_in_the_past": is_in_the_past,
        },
    )
