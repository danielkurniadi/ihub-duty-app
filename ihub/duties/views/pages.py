from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from duties.serializers import DutySerializer
from users.serializers import UserSerializer
from duties.models import (
    Duty, DutyManager
)

User = get_user_model()
duty_manager = DutyManager.load()

@login_required
def duty_template_view(request):
    """Render duty page for on-duty or idle user
    """
    if request.method == 'GET':
        return render(request, 'duty.html')
