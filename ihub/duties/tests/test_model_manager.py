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

    def test_manager_singularity_creation(self):
        """Test manager model is a singular db model, and load() will give same reference to
        the db row in manager table, hence ORM objects of manager have the same state everywhere.
        """
        # Step 1: initialise duty_manager1 & duty_manager2
        duty_manager1 = DutyManager.load()
        duty_manager2 = DutyManager.load()

        # Step 1b: verify duty_manager1 and duty_manager2 has no active_duties
        self.assertEqual(duty_manager1.active_duties.count(), 0)
        self.assertEqual(duty_manager2.active_duties.count(), 0)

        # Step 1c: check both refer to the same row by id
        self.assertEqual(duty_manager1, duty_manager2)
        self.assertEqual(duty_manager1.id, 1)
        self.assertEqual(duty_manager2.id, 1)

        # Step 2: modify duty_manager1 by adding active duty
        duty1 = duty_manager1.active_duties.create()

        # Step 2b: verify duty_manager1 associated with duty1 and 
        # duty_manager2 has duty1 as well (no need refresh_from_db)
        self.assertEqual(duty_manager1.active_duties.count(), 1)
        self.assertEqual(duty_manager2.active_duties.count(), 1)
        self.assertTrue(duty_manager2.active_duties.filter(pk=duty1.id).exists())

        # Step 3: create duty_manager3
        duty_manager3 = DutyManager.load()

        # Step 3b: verify duty_manager3 has duty1 as well.
        self.assertEqual(duty_manager3.active_duties.count(), 1)
        self.assertTrue(duty_manager3.active_duties.filter(pk=duty1.id).exists())

        # Step 4: remove duty1
        duty_manager1.active_duties.remove(duty1)
        self.assertEqual(duty_manager1.active_duties.count(), 0)

        # Step 4b: verify other manager also updated and lost association to duty1
        self.assertEqual(duty_manager2.active_duties.count(), 0)
        self.assertEqual(duty_manager3.active_duties.count(), 0)

        # Step 4c: create one more manager and verify
        duty_manager4 = DutyManager.load()
        self.assertEqual(duty_manager4.active_duties.count(), 0)

    def test_manager_start_duty(self):
        """Test given a user, manager is able to start a duty with that user.
        Foreign key relations are formed between user-duty and duty-manager.
        """
        # Step 1: initialise user & duty manager
        user = self.generate_ihub_user()
        duty_manager = DutyManager.load()

        # Step 1b: verify duty is empty initially
        self.assertEqual(user.duty_set.count(), 0)
        self.assertEqual(duty_manager.active_duties.count(), 0) 

        # Step 2: create duty with user using duty manager
        duty = duty_manager.start_duty(user)

        # Step 3: verify duty is created for user by duty manager
        self.assertEqual(user.duty_set.count(), 1)
        self.assertEqual(duty_manager.active_duties.count(), 1)

        # Step 3b: verify user associated to duty in duty manager
        self.assertEqual(duty, duty_manager.get_duties_of(user)[0])

    def test_manager_start_duty_with_debtee(self):
        """Test given a user buying duty debt from debtee, manager is able to
        start a duty with foreign key to user and to debtee. 
        """
        # Step 1: initialise user, debtee, and duty manager
        user = self.generate_ihub_user()
        debtee = self.generate_ihub_user()
        duty_manager = DutyManager.load()

        # Step 1b: verify duty is empty initially
        self.assertEqual(user.duty_set.count(), 0)
        self.assertEqual(duty_manager.active_duties.count(), 0)
        self.assertEqual(debtee.duty_debt_set.count(), 0)

        # Step 2: create duty debt with user and debtee via duty manager
        duty = duty_manager.start_duty(user, debtee=debtee)

        # Step 3: verify duty debt is created for debtee in duty manager
        self.assertEqual(user.duty_set.count(), 1)
        self.assertEqual(duty_manager.active_duties.count(), 1)
        self.assertEqual(debtee.duty_debt_set.count(), 1)

        # Step 3b: verify duty started is associated as debt to debtee
        self.assertIn(duty, debtee.duty_debt_set.all())
        self.assertTrue(debtee.duty_debt_set.filter(pk=duty.id).exists())

    def test_manager_filter_finished_duties(self):
        """Test given several duties which some has been finished, manager is able to
        filter finished duties.
        """
        # Step 1: initialise 4 duties
        duty1 = Duty.objects.create()
        duty2 = Duty.objects.create()
        duty3 = Duty.objects.create()
        duty4 = Duty.objects.create()
        duty_manager = DutyManager.load()

        # Step 1b: associate duties with duty manager as active duties
        duty_manager.active_duties.add(duty1, duty2, duty3, duty4,
            bulk=True)
        
        # Step 2: mark duty1 & duty2 as finished
        duty1.force_finish_duty()
        duty2.force_finish_duty()

        # Step 3: manager filter finished duty
        finished_duties = duty_manager.filter_finished_duties()
        
        # Step 3b: verify finished duties are filtered
        self.assertEqual(finished_duties.count(), 2)
        self.assertIn(duty1, finished_duties)
        self.assertIn(duty2, finished_duties)

        # duty_manager.active_duties.remove(*finished_duties, bulk=True)
        # self.assertEqual(duty_manager.active_duties.count(), 2)

    def test_manager_remove_finished_duties(self):
        """Test given several duties which some has been finished, manager is able to
        filter and remove the unfinished duties.
        """
        # Step 1: initialise 4 duties
        duty1 = Duty.objects.create()
        duty2 = Duty.objects.create()
        duty3 = Duty.objects.create()
        duty4 = Duty.objects.create()
        duty_manager = DutyManager.load()

        # Step 1b: associate duties with duty manager as active duties
        duty_manager.active_duties.add(duty1, duty2, duty3, duty4,
            bulk=True)
        
        # Step 2: mark duty1 & duty2 as finished
        duty1.force_finish_duty()
        duty2.force_finish_duty()

        # Step 3: manager filter finished duty
        finished_duties = duty_manager.remove_finished_duties()

        # Step 3b: verify finished duties are removed
        self.assertEqual(finished_duties.count(), 2)
        self.assertIn(duty1, finished_duties)
        self.assertIn(duty2, finished_duties)
        self.assertEqual(duty_manager.active_duties.count(), 2)

        # Step 3c: verify unfinished duties are still associated with duty manager
        self.assertIn(duty3, duty_manager.active_duties.all())
        self.assertIn(duty4, duty_manager.active_duties.all())

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

    def tearDown(self):
        pass