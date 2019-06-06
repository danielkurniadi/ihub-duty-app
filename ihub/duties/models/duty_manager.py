from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from utils.singletons import SingletonModel

User = get_user_model()

class DutyManager(SingletonModel):
    
    pass
