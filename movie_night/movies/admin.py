from django.contrib import admin

from movies.models import Movie, MovieNight, MovieNightInvitation, SearchTerm, Genre

admin.site.register(Movie)
admin.site.register(MovieNight)
admin.site.register(MovieNightInvitation)
admin.site.register(SearchTerm)
admin.site.register(Genre)
