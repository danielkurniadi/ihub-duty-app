from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from utils import RandomSupport
from duties.models import (
    Duty, DutyManager
)

User = get_user_model()

class DutyManagerTests(TestCase, RandomSupport):
    """Tests Duty Manager functionalities & behavior.
    """

    def setUp(self):
        pass

    def test_manager_start_duty(self):
        """Test given a user, manager is able to start a duty with that user.
        Foreign key relations are formed between user-duty and duty-manager.
        """
        pass

    def test_manager_start_duty_with_debtee(self):
        """Test given a user buying duty debt from debtee, manager is able to
        start a duty with foreign key to user and to debtee. 
        """
        pass

    def test_manager_filter_finished_duties(self):
        """Test given several duties which some has been finished, manager is able to
        filter finished duties.
        """
        pass
    
    def test_manager_remove_finished_duties(self):
        """Test given several duties which some has been finished, manager is able to
        filter and remove the unfinished duties.
        """
        pass

    #########################################################################################

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

