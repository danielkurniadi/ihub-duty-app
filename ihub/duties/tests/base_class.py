from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient

from duties.models import Duty, DutyManager
from utils.random_supports import RandomSupport

User = get_user_model()


class BaseTestCaseMixin(RandomSupport):
	"""Base TestCase class mixin
	"""
	def generate_ihub_user(self, email=None, matric=None, password=None):
		"""Helper that create mock user with lowest permission.

		Args:
			name (str): name for user, generate name if None
			email (str): email for credential, generate email if None
			password (str): password for credential, generate password if None

		Return:
			user (User)
		"""
		# random generate value if not specified
		name = self.generate_name()
		email = email if email else self.generate_email()
		matric = matric if matric else self.generate_matric()
		password = password if password else self.generate_alphanumeric(10)

		# create user with value specified
		user = User.objects.create_user(email, password, matric, name=name)
		user.save()

		return user

	def verify_default_duty_timings(self, duty):
		"""Given duty uses a default timing for start & end of
		each tasks, verify that it is indeed True.

		Args:
			duty (Duty): duty to be verified as having default timing
		"""
		# duty timings
		start = duty.duty_start
		end = duty.duty_end

		# default duty time mark start
		delta_task1_start = timedelta(minutes=Duty.TASK1_MARK)
		delta_task2_start = timedelta(minutes=Duty.TASK2_MARK)
		delta_task3_start = timedelta(minutes=Duty.TASK3_MARK)

		# default duty time mark end
		task_window = timedelta(minutes=Duty.TASK_WINDOW)
		duty_window = timedelta(minutes=Duty.DUTY_DURATION)

		# check duty's tasks starting time
		self.assertEqual(duty.task1_start, start + delta_task1_start)
		self.assertEqual(duty.task2_start, start + delta_task2_start)
		self.assertEqual(duty.task3_start, start + delta_task3_start)

		# check duty's tasks ending time
		self.assertEqual(end, start + duty_window)
		self.assertEqual(duty.task1_end, duty.task1_start + task_window)
		self.assertEqual(duty.task2_end, duty.task2_start + task_window)
		self.assertEqual(duty.task3_end, duty.task3_start + task_window)


class BaseDutyTestCase(TestCase, BaseTestCaseMixin):
	"""Super class of any DutyTests
	"""
	pass


class BaseDutyAPITestCase(APITestCase, BaseTestCaseMixin):
	"""Super class of APITests for Duty
	"""
	def prepare_manager(self):
		self.duty_manager = DutyManager.load()

	def prepare_login_user(self, idx=None):
		"""Generate mock user and authenticate
		"""
		email = self.generate_email()
		password = self.generate_alphanumeric(10)
		user = self.generate_ihub_user(email=email, password=password)

		# authenticate and login
		is_login = self.client.login(email=email, password=password)
		user.refresh_from_db()

		setattr(self, 'user%d' % idx, user)
		setattr(self, 'pass%d' % idx, password)
		
		if not hasattr(self, 'idxs'):
			self.idxs = []
		self.idxs.append(idx)

	def cleanup_mock_user(self):
		if not hasattr(self, 'idxs'):
			return

		for idx in self.idxs:
			delattr(self, 'user%d' % idx)
			delattr(self, 'pass%d' % idx)
