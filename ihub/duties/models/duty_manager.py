from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from utils.singletons import SingletonModel
from duties.errors import MaxDutyCountError

User = get_user_model()

class DutyManager(SingletonModel):
    MAX_DUTY = 1

    ########################################
    # Active Duties
    ########################################

    def start_duty(self, user, debtee=None):
        # check MAX_DUTY threshold condition
        if self.duties_count() < DutyManager.MAX_DUTY:
           duty = self.active_duties.create()
           user.duty_set.add(duty)
           user.save(); duty.save()
           return duty
        # MAX_DUTY condition fail, raise error
        raise MaxDutyCountError

    def filter_finished_duties(self):
        # filter duties which end has passed
        finished_duties = self.active_duties.filter(duty_end__lte=timezone.now())
        return finished_duties

    def remove_finished_duties(self):
        # filter duties which end has passed
        finished_duties = tuple(
            duty for duty in self.filter_finished_duties()
        )
        # remove all relationships to finished duties w/o deleting object
        if finished_duties:
            self.active_duties.remove(*finished_duties, bulk=True)
        return finished_duties # tuple

    def get_duties_of(self, user):
        user_active_duties = tuple(
            duty for duty in self.active_duties.filter(user__email=user.email)
        )
        return user_active_duties # tuple

    def remove_duties_of(self, user):
        if user.duty_set.count() == 0:
            return tuple()
        user_active_duties = self.get_duties_of(user)
        # remove if any duty of user in manager 
        if user_active_duties:
            self.active_duties.remove(*user_active_duties, bulk=True)
        return user_active_duties # tuple

    ########################################
    # Onduty User
    ########################################

    def get_onduty_users(self):
        onduty_users = self.active_duties.values_list('user')
        return onduty_users

    def is_onduty(self, user):
        onduty_users = self.get_onduty_users()
        return (user in onduty_users)
