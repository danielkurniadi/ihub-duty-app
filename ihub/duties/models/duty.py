from datetime import datetime, timedelta
from django.db import models

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Duty(models.Model):
    # Task duration constant (minutes)
    TASK_WINDOW = 30

    # Task start mark from duty_start
    TASK1_MARK = 30
    TASK2_MARK = 90
    TASK3_MARK = 150

    # Duty Duration
    DUTY_DURATION = 180

    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        blank=True, null=True)

    debtee = models.ForeignKey(User, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='duty_debt_set')

    duty_start = models.DateTimeField(editable=False)
    task1_start = models.DateTimeField(editable=False)
    task2_start = models.DateTimeField(editable=False)
    task3_start = models.DateTimeField(editable=False)

    duty_end =  models.DateTimeField(editable=False)
    task1_end = models.DateTimeField(editable=False)
    task2_end = models.DateTimeField(editable=False)
    task3_end = models.DateTimeField(editable=False)

    last_active = models.DateTimeField(null=True, blank=True)

    ########################################
    # models.Model methods override
    ########################################

    def save(self, *args, **kwargs):
        now = timezone.now()
        # Creation
        if not self.id:
            # starting marker
            self.duty_start = now
            self.task1_start = now + timedelta(minutes=Duty.TASK1_MARK)
            self.task2_start = now + timedelta(minutes=Duty.TASK2_MARK)
            self.task3_start = now + timedelta(minutes=Duty.TASK3_MARK)
            # ending marker
            self.duty_end = now + timedelta(minutes=Duty.DUTY_DURATION)
            self.task1_end = self.task1_start + timedelta(minutes=Duty.TASK_WINDOW)
            self.task2_end = self.task2_start + timedelta(minutes=Duty.TASK_WINDOW)
            self.task3_end = self.task3_start + timedelta(minutes=Duty.TASK_WINDOW)
            # last active
            self.last_active = now
        # Update save
        return super(Duty, self).save(*args, **kwargs)

    ########################################
    # Python native methods override
    ########################################

    def __str__(self):
        if not self.user:
            return ("Zombie Duty Instance from time |{: %d %b %Y, %H:%M:%S}| to "
            "|{: %d %b %Y, %H:%M:%S}|".format(self.duty_start, self.duty_end))

        if self.is_finished():
            return ("Past duty Instance from time |{: %d %b %Y, %H:%M:%S}| to "
            "|{: %d %b %Y, %H:%M:%S}| by {}".format(
                self.duty_start, self.duty_end, self.user.name))

        return ("Active duty Instance from time |{: %d %b %Y, %H:%M:%S}| to "
            "|{: %d %b %Y, %H:%M:%S}| by {}".format(
                self.duty_start, self.duty_end, self.user.name))

    ########################################
    # Duty methods
    ########################################

    def is_finished(self):
        return self.duty_end <= timezone.now()

    # Caution: warp duty_end time back to now
    def force_finish_duty(self):
        if self.is_finished != True:
            self.update_duty_end(timezone.now())

    def update_duty_end(self, duty_end):
        # update the task end if task_end > new duty_end
        if self.task1_end < duty_end:
            self.task1_end = duty_end
        if self.task2_end < duty_end:
            self.task2_end = duty_end
        if self.task3_end < duty_end:
            self.task3_end = duty_end
        # finally update the duty_end
        self.duty_end = duty_end
