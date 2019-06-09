"""
Module errors.py

All possible errors and exceptions should be put here.
Exceptions are used and catched in the views, or in the serializers.

Try catch method will be used to defend against erroneous inputs with
a given context/situation. Then an appropriate HTTP status will be given 
as a response in occurence of the corresponding exception.

"""
from datetime import datetime, timedelta

class CannotStartOverOngoingDuty(Exception):
    def __init__(self):
        self.message = ("Existing duty from other user is still ongoing"
            "and must be cleared first before starting new duty.")
        super().__init__(self.message)


class UnfinishedDutyError(Exception):
    def __init__(self, duty_end=None):
        duty_end = "|UNKNOWN TIME|" if not duty_end else "|{: %d %b %Y, %H:%M:%S}|".format(duty_end)
        self.message = ("User's ongoing duty hasn't reach the duty end time but try to create new duty."
            "Finish user's active duty first!" % duty_end)
        super().__init__(self.message)


class MaxDutyCountError(Exception):
    def __init__(self):
        self.message = "Maximum duty count handled by manager is reached. Cannot add more duty."
        super().__init__(self.message)
