from django_registration.forms import RegistrationForm as DefaultRegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from movienight_auth.models import User

class RegistrationForm(DefaultRegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Register"))
