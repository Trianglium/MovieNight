from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from movies.models import MovieNight, MovieNightInvitation

UserModel = get_user_model()


class SearchForm(forms.Form):
    term = forms.CharField(required=False)


class MovieNightForm(forms.ModelForm):
    class Meta:
        model = MovieNight
        fields = ["start_time"]


class InviteeForm(forms.Form):
    email = forms.EmailField()

    _user = False

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            # cache for later
            self._user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise ValidationError(f"User with email address '{email}' was not found.")

        return email


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = MovieNightInvitation
        fields = ["is_attending"]

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields["is_attending"].label = "Attending?"
