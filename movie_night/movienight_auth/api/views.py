from rest_framework import generics

from movienight_auth.api.serializers import UserSerializer
from movienight_auth.models import User


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "email"
