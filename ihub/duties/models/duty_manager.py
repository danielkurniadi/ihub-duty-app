from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from utils.singletons import SingletonModel
from bridge.decorators import manager_refresh
from bridge.constants.errors import (
	MaxDutyCountError, UnfinishedDutyError
)

User = get_user_model()

class ManagerMixin(object):
	"""Manager mixin contains basic manager capabilities and interfaces
	"""
	def refresh(self):
		raise NotImplementedError

class DutyManager(SingletonModel, ManagerMixin):
	MAX_DUTY = 1

	########################################
	# Active Duties
	########################################

	@manager_refresh
	def start_duty(self, user, debtee=None):
		# check MAX_DUTY threshold condition
		if self.active_duties.count() >= DutyManager.MAX_DUTY:
			raise MaxDutyCountError
		# check user has no active duty before
		if self.is_onduty(user):
			duty_end = self.get_duties_of(user)[0].duty_end # take the first active
			raise UnfinishedDutyError(duty_end=duty_end)

		duty = self.active_duties.create()
		user.duty_set.add(duty)
		if debtee:
			debtee.duty_debt_set.add(duty)
			debtee.save()
		user.save(); duty.save()
		return duty

	def filter_finished_duties(self):
		# filter duties which end has passed
		finished_duties = self.active_duties.filter(duty_end__lte=timezone.now())
		return finished_duties

	def remove_finished_duties(self):
		# filter duties which end has passed
		finished_duties = self.filter_finished_duties()
		# remove all relationships to finished duties w/o deleting object
		if finished_duties:
			self.active_duties.remove(*finished_duties, bulk=True)
		return finished_duties # tuple

	@manager_refresh
	def get_duties_of(self, user):
		user_active_duties = tuple(
			duty for duty in self.active_duties.filter(user__email=user.email)
		)
		return user_active_duties # tuple

	def remove_duties_of(self, user):
		# check defensively if user ever has duty
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

	@manager_refresh
	def get_onduty_user_ids(self):
		onduty_user_ids = self.active_duties.values_list('user') # QuerySet<[(pk,), (pk,), ...]>
		return map(lambda tup: tup[0], onduty_user_ids)

	def is_onduty(self, user):
		onduty_user_ids = self.get_onduty_user_ids() # map object
		return (user.id in onduty_user_ids)

	########################################
	# General Methods
	########################################

	def refresh(self):
		self.remove_finished_duties()

	def reset(self):
		self.active_duties.clear()
