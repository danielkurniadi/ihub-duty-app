from datetime import datetime, timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from duties.tests.base_class import BaseDutyTestCase
from duties.models import (
    Duty,
)

User = get_user_model()

class DutyTests(BaseDutyTestCase):
    """Test Duty model functionalities
    """

    def setUp(self):
        """Setup mock for each test
        """
        pass

    def test_create_zombie_duty(self):
        """Test create zombie duty (w/o user and debtee)
        """
        # initially no duty created
        self.assertEqual(Duty.objects.count(), 0)

        # create new Duty without user nor debtee
        duty = Duty.objects.create()

        # verify duty count increases by 1
        self.assertEqual(Duty.objects.count(), 1)

        # verify default duty timings
        self.verify_default_duty_timings(duty)

        # verify no user nor debtee at the moment
        self.assertIsNone(duty.user)
        self.assertIsNone(duty.debtee)

    def test_create_duty_with_user(self):
        """Test create duty with user and without debtee
        """
        # initially no duty created
        self.assertEqual(Duty.objects.count(), 0)

        # create new Duty with user but no debtee
        user = self.generate_ihub_user()
        duty = Duty.objects.create(user=user)

        # verify user's duty count increases by 1
        self.assertEqual(Duty.objects.count(), 1)
        self.assertEqual(user.duty_set.count(), 1)
        
        # verify duty's user is user by ORM pointer
        # Careful!: (user.duty_set.get(pk=duty.id) is not duty) by ORM pointer!
        self.assertIsNotNone(duty.user)
        self.assertIs(duty.user, user)

        # verify default duty timings
        self.verify_default_duty_timings(duty)

        # verify duty has no debtee (not a subtitute), and user has not debted any duty
        self.assertIsNone(duty.debtee)
        self.assertEqual(user.duty_debt_set.count(), 0)

    def test_create_anonymous_duty_debt(self):
        """Test user can sell duty debt to no one. Duty debt has anonymous owner
        since no one is buying the duty debt.
        """
        debtee = self.generate_ihub_user()

        # verify user has no duty previously
        self.assertEqual(debtee.duty_debt_set.count(), 0)

        # create debted duty
        debted_duty = debtee.duty_debt_set.create()
        duty_id = debted_duty.id
        self.assertEqual(debtee.duty_debt_set.count(), 1)

        # verify duty
        self.assertEqual(
            debted_duty, 
            debtee.duty_debt_set.get(pk=duty_id)
        )

    def test_user_create_add_multiple_duties(self):
        """Test user object can create and have multiple duties,
        can indebting duties, or sell duty debt.
        """
        user = self.generate_ihub_user()

        # verify user has no duty previously
        self.assertEqual(user.duty_set.count(), 0)

        # user create his own duty1
        duty1 = user.duty_set.create()
        self.assertEqual(user.duty_set.count(), 1)

        # create user2 & user3
        user2 = self.generate_ihub_user()
        user3 = self.generate_ihub_user()

        # user2 & user3 create debted duty
        duty2 = user2.duty_debt_set.create()
        duty3 = user3.duty_debt_set.create()

        # indebted duties are sold to debtor user
        user.duty_set.add(duty2)
        user.duty_set.add(duty3)

        # verify user has 3 duties
        self.assertEqual(user.duty_set.count(), 3)

        duty2 = user.duty_set.get(pk=duty2.id)
        duty3 = user.duty_set.get(pk=duty3.id)

        # verify user2 & user3 are indebted by user
        self.assertEqual(duty2.debtee, user2)
        self.assertEqual(duty3.debtee, user3)

    def test_force_end_duty(self):
        """Test force warp duty_end to now works and mark duty as finished
        """
        duty = Duty.objects.create()
        
        # verify duty uses default timings
        self.verify_default_duty_timings(duty)

        # back warp duty_end to force finish
        now = timezone.now().replace(second=0, microsecond=0)
        duty.force_finish_duty()

        # verify duty is finished
        self.assertEqual(duty.duty_end.replace(second=0, microsecond=0), now)
        self.assertTrue(duty.is_finished())

    def test_delete_zombie_duty(self):
        """Test deleting zombie duty works. Accessing deleted duty by id will
        raise Duty.DoesNotExist exceptions.
        """
        # initially no duty
        self.assertEqual(Duty.objects.count(), 0)
        
        duty = Duty.objects.create()
        duty_id = duty.id
        
        # verify duty is created
        self.assertEqual(Duty.objects.count(), 1)
        Duty.objects.get(pk=duty_id)

        # Step 1: delete duty
        duty.delete()
        
        # Step 2: verify no longer can access duty from db by pk
        with self.assertRaises(Duty.DoesNotExist):
            Duty.objects.get(pk=duty_id)
        
        # Step 3: verify no longer can refresh duty
        with self.assertRaises(Duty.DoesNotExist):
            duty.refresh_from_db()

    def test_delete_duty_with_user(self):
        """Test deleting duty with user will delete user object's reference
        to the duty.Accessing deleted duty from user will raise Duty.DoesNotExist exceptions.
        """
        user = self.generate_ihub_user()

        # initially user has no duty
        self.assertEqual(user.duty_set.count(), 0)

        # user create his own duty
        duty = user.duty_set.create()
        duty_id = duty.id

        # verify user has one duty
        self.assertEqual(user.duty_set.count(), 1)

        # verify duty is associated with user
        self.assertEqual(duty.user, user)

        # Step 1: delete duty
        duty.delete()

        # Step 2: query user's duty pk=duty_id, then expect Duty.DoesNotExist
        with self.assertRaises(Duty.DoesNotExist):
            user.duty_set.get(pk=duty_id)
        
        # Step 3: verify user has 0 duty
        self.assertEqual(user.duty_set.count(), 0)

    def test_delete_anonymous_duty_debt(self):
        """Test deleting debted duty from debtee to anonymous user.
        """
        debtee = self.generate_ihub_user()

        # initially debtee has no debt
        self.assertEqual(debtee.duty_debt_set.count(), 0)

        # debtee create a duty debt
        duty_debt = debtee.duty_debt_set.create()
        duty_id = duty_debt.id

        # verify debtee has one debt
        self.assertEqual(debtee.duty_debt_set.count(), 1)

        # verify debt is associated with debtee
        self.assertEqual(duty_debt.debtee, debtee)

        # Step 1: delete debt duty
        duty_debt.delete()

        # Step 2: query debtee's debt pk=duty_id, then expect Duty.DoesNotExist
        with self.assertRaises(Duty.DoesNotExist):
            debtee.duty_debt_set.get(pk=duty_id)
        
        # Step 3: verify debtee has 0 debt
        self.assertEqual(debtee.duty_debt_set.count(), 0)
    
    def test_delete_multiple_duty(self):
        """Test deleting several duty debt which are indebted to user/debtor
        and duty of user's own.
        """
        user = self.generate_ihub_user()
        debtee1 = self.generate_ihub_user()
        debtee2 = self.generate_ihub_user()

        # initially debtee has no debt
        self.assertEqual(debtee1.duty_debt_set.count(), 0)
        self.assertEqual(debtee2.duty_debt_set.count(), 0)

        # Step1: user (debtor) create and has his own duty
        duty = user.duty_set.create()
        self.assertEqual(user.duty_set.count(), 1)

        # Step2: debtees create duty debts
        duty1 = debtee1.duty_debt_set.create()
        duty2 = debtee2.duty_debt_set.create()

        # Step3: user (debtor) buy the debts
        user.duty_set.add(duty1, duty2)

        # verify user has 3 duties, debtee each has 1 debt
        self.assertEqual(user.duty_set.count(), 3)
        self.assertEqual(debtee1.duty_debt_set.count(), 1)
        self.assertEqual(debtee2.duty_debt_set.count(), 1)

        # Step 4: delete duty1 and verify debtee1 not associated with duty1
        duty1_id = duty1.id
        duty1.delete()
        self.assertFalse(debtee1.duty_debt_set.filter(pk=duty1_id).exists())

        # Step 4b: delete duty2 and verify debtee2 not associated with duty2
        duty2_id = duty2.id
        duty2.delete()
        self.assertFalse(debtee2.duty_debt_set.filter(pk=duty2_id).exists())

        # Step 4c: verify user back to 1 duty
        self.assertEqual(user.duty_set.count(), 1)
        self.assertTrue(user.duty_set.filter(pk=duty.id).exists())

    def test_duty_remove_user_relation(self):
        """Tests removing duty foreign key from user manager works.
        Duty still need to refresh db.
        """
        user = self.generate_ihub_user()
        duty = user.duty_set.create()

        # Step 1: initially duty is associated with user
        self.assertEqual(user.duty_set.count(), 1)
        self.assertTrue(user.duty_set.filter(pk=duty.id).exists())
        self.assertEqual(duty.user, user)

        # Step 2: remove duty
        user.duty_set.remove(duty)

        # Step 2b: verify duty still exists in db
        duty.refresh_from_db() # Important!
        self.assertIsNotNone(duty)

        # Step 2c: verify user is not associated with duty
        self.assertEqual(user.duty_set.count(), 0)
        self.assertFalse(user.duty_set.filter(pk=duty.id).exists())

        # Step 2d: verify duty has no user:
        self.assertIsNone(duty.user) # Need to refresh duty from db!

    def test_duty_remove_debtee_relation(self):
        """Tests removing duty foreign key from a debtee's user manager works.
        Duty still need to refresh db.
        """
        debtee = self.generate_ihub_user()
        duty = debtee.duty_debt_set.create()

        # Step 1: initially duty debt is associated with debtee
        self.assertEqual(debtee.duty_debt_set.count(), 1)
        
