from django.urls import path

from movienight_auth.api.views import UserDetail

urlpatterns = [
    path("users/<str:email>", UserDetail.as_view(), name="user-detail"),
]
