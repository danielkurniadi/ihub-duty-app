from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'matric') # password is automatically added by UserCreationForm
