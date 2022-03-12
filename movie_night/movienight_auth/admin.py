from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from movienight_auth.models import User

class MovieNightUserAdmin(UserAdmin):
    pass


admin.site.register(User, MovieNightUserAdmin)
