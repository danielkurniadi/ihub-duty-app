from rest_framework import serializers

from duties.models import Duty
from users.serializers import UserSerializer

class DutySerializer(serializers.ModelSerializer):
    """Duty object serializer
    """
    debtee = UserSerializer()

    class Meta:
        model = Duty
        fields = (
            'duty_start', 'duty_end', 
            'task1_start', 'task1_end',
            'task2_start', 'task2_end',
            'task3_start', 'task3_end',
            'last_active', 'debtee',
        )
