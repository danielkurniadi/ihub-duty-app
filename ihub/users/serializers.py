from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'matric')
