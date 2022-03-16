"""movienight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django_registration.backends.activation.views import RegistrationView

import movienight_auth.views
import movies.views
from movienight_auth.forms import RegistrationForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/profile/", movienight_auth.views.profile, name="profile"),
    path(
        "accounts/register/",
        RegistrationView.as_view(form_class=RegistrationForm),
        name="django_registration_register",
    ),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", movies.views.index),
    path("movie-nights/", movies.views.movie_night_list, name="movie_night_list_ui"),
    path(
        "movie-nights/<int:pk>/",
        movies.views.movie_night_detail,
        name="movie_night_detail_ui",
    ),
    path("search/", movies.views.movie_search, name="movie_search_ui"),
    path("movies/<slug:imdb_id>/", movies.views.movie_detail, name="movie_detail_ui"),
    path("api/v1/", include("movienight.api_urls")),
]
