from django.urls import reverse

from rest_framework import status

from duties.serializers import DutySerializer
from duties.models import Duty, DutyManager

from duties.tests.base_class import BaseDutyAPITestCase

class DutiesAPITests(BaseDutyAPITestCase):
	"""Tests endpoints and api views in `duties/api/`.
	"""

	def setUp(self):
		self.prepare_manager()
		self.addCleanup(self.duty_manager.active_duties.clear)

	########################################
	# Unit Tests
	########################################

	def test_api_create_active_duty(self):
		"""Test API starting duty without debtee works and saved to database
		"""
		# prepare mock user
		self.prepare_login_user(1)
		user_id = self.client.session['_auth_user_id']

		# check if logged in & verify no active duties
		self.assertEqual(int(user_id), self.user1.id)

		# Step 1: user verify no active duty
		self.assertEqual(self.user1.duty_set.count(), 0)

		# Step 2: POST start duty using api call
		response = self.client.post(reverse('duties:duty-create'))
		self.assertIn(response.status_code,
			[status.HTTP_200_OK, status.HTTP_201_CREATED]
		)

		# Step 3: verify started duty
		duty_resp = response.data['payload']
		duty1 = self.duty_manager.get_duties_of(self.user1)[0]
		serialized = DutySerializer(duty1)
		self.assertEqual(duty_resp, serialized.data)

	def test_api_get_active_duty(self):
		"""Test API get ongoing/active duty in duty manager
		"""
		# prepare mock user
		self.prepare_login_user(1)
		user_id = self.client.session['_auth_user_id']

		# check if logged in & verify no active duties
		self.assertEqual(int(user_id), self.user1.id)

		# Step 1: user verify no active duty
		self.assertEqual(self.user1.duty_set.count(), 0)

		# Step 2: create duty using manager directly
		duty1 = self.duty_manager.start_duty(self.user1)
		self.assertEqual(self.duty_manager.active_duties.count(), 1)
		self.assertEqual(self.user1.duty_set.count(), 1)

		# Step 3: GET api call to active duty by user1
		response = self.client.get(reverse('duties:duty-details'))
		self.assertIn(response.status_code,
			[status.HTTP_200_OK, status.HTTP_201_CREATED]
		)

		# Step 3b: verify GET response
		duty_resp = response.data['payload'][0] # OrderedDict({...})[0]
		serialized = DutySerializer(duty1)
		self.assertEqual(duty_resp, serialized.data)

	########################################
	# Behavioral Tests
	########################################

	def test_api_create_get_active_duty(self):
		"""Test API where user is logged from start to end:
		1. GET active duties of user, expect HTTP4xx no duty initially
		2. POST user create duty in manager successful
		3. GET active duties of user in manager successful
		4. POST create duty, user expect HTTP4xx cannot create duty if one already ongoing
		"""
		# prepare mock user
		self.prepare_login_user(1)
		user_id = self.client.session['_auth_user_id']

		# check if logged in & verify no active duties
		self.assertEqual(int(user_id), self.user1.id)
		self.assertEqual(self.user1.duty_set.count(), 0)
		self.assertEqual(self.duty_manager.active_duties.count(), 0)

		# Step 1: GET active duties of user, expect HTTP4xx no duty initially
		response1 = self.client.get(reverse('duties:duty-details'))
		self.assertIn(response1.status_code,
			[status.HTTP_400_BAD_REQUEST]
		)
		self.assertEqual(self.user1.duty_set.count(), 0)

		# Step 2: POST user create duty in manager
		response2 = self.client.post(reverse('duties:duty-create'))
		self.assertIn(response2.status_code,
			[status.HTTP_200_OK, status.HTTP_201_CREATED]
		)
		self.assertIsNotNone(response2.data['payload'])
		self.assertEqual(self.user1.duty_set.count(), 1)
		self.assertTrue(self.duty_manager.is_onduty(self.user1))

		# Step 3: GET active duties of user in manager successful
		response3 = self.client.get(reverse('duties:duty-details'))
		self.assertIn(response3.status_code,
			[status.HTTP_200_OK]
		)
		self.assertIsNotNone(response3.data['payload'][0])

		# Step 4: POST create duty, user expect HTTP4xx cannot create duty if one already ongoing
		response4 = self.client.post(reverse('duties:duty-create'))
		self.assertIn(response4.status_code, 
			[status.HTTP_400_BAD_REQUEST]
		)

		# verify everything is still ok 
		self.assertEqual(self.user1.duty_set.count(), 1)
		self.assertTrue(self.duty_manager.is_onduty(self.user1))

	def test_api_create_get_active_duty_with_relogin(self):
		"""Test API where user is logged from start but relogin in after Step2:
		1. GET active duties of user, expect HTTP4xx no duty initially
		2. POST user create duty in manager successful
		3. Logout and re-login user
		3. GET active duties of user in manager successful
		"""
		# prepare mock user
		self.prepare_login_user(1)
		user_id = self.client.session['_auth_user_id']

		# check if logged in & verify no active duties
		self.assertEqual(int(user_id), self.user1.id)
		self.assertEqual(self.user1.duty_set.count(), 0)
		self.assertEqual(self.duty_manager.active_duties.count(), 0)

		# Step 1: GET active duties of user, expect HTTP4xx no duty initially
		response1 = self.client.get(reverse('duties:duty-details'))
		self.assertIn(response1.status_code,
			[status.HTTP_400_BAD_REQUEST]
		)
		self.assertEqual(self.user1.duty_set.count(), 0)

		# Step 2: POST user create duty in manager successful
		response2 = self.client.post(reverse('duties:duty-create'))
		self.assertIn(response2.status_code,
			[status.HTTP_200_OK, status.HTTP_201_CREATED]
		)
		self.assertIsNotNone(response2.data['payload'])
		self.assertEqual(self.user1.duty_set.count(), 1)
		self.assertTrue(self.duty_manager.is_onduty(self.user1))

		# Step 3: Logout
		self.client.logout()
		self.assertIsNone(self.client.session.get('_auth_user_id'))

		# Step 3b: GET HTTP401 or 403 to verify client no longer logged in
		response3 = self.client.get(reverse('duties:duty-details'))
		self.assertIn(
			response3.status_code,
			[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
		)

		# Step 3c: re-Login and verify logged in
		is_login = self.client.login(email=self.user1.email, password=self.pass1)
		user_id = self.client.session['_auth_user_id']
		self.assertTrue(is_login)
		self.assertEqual(int(user_id), self.user1.id)

		# Step 4: GET active duties of user in manager successful
		response4 = self.client.get(reverse('duties:duty-details'))
		self.assertIn(
			response4.status_code,
			[status.HTTP_200_OK]
		)
		self.assertIsNotNone(response4.data['payload'][0])

	####################################################################################################

	def tearDown(self):
		self.cleanup_mock_user()
