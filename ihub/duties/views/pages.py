from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

from duties.serializers import DutySerializer
from users.serializers import UserSerializer
from duties.models import (
    Duty, DutyManager
)

User = get_user_model()

try:
    duty_manager = DutyManager.load()
except:
    pass


@login_required
def duty_template_view(request):
    """Render duty page for on-duty or idle user
    """
    if request.method == 'GET':
        user = request.user
        if duty_manager.is_onduty(user):
            return render(request, 'onduty.html')
        return render(request, 'getstarted.html')
    else:
        return HttpResponseNotAllowed("Wrong Method")
