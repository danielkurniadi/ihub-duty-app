from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from duties.models import (
    Duty, DutyManager
)
from duties.serializers import DutySerializer
from users.serializers import UserSerializer
from bridge.constants.errors import (
	MaxDutyCountError, UnfinishedDutyError
)

User = get_user_model()
duty_manager = DutyManager.load()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def duty_api_start_view(request):
    # preprocessing
    duty_manager.remove_finished_duties()

    user = request.user
    debtee = None

    # check debtee data if specified, then if do
    # also check if data exists/matches to any users other than the user
    debtee_params = request.data.get('debtee')
    if debtee_params:
        debtee = get_object_or_404(User, **debtee_params)
        if debtee == user:
            return Response({
                'success': False,
                'message': "Cannot specify yourself as in-debt friend. Do you mistype friend matric no. with yours?",
                'now': "{:%m/%d/%Y %H:%M:%S}".format(timezone.localtime()),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # start duty with duty manager, user, and debtee(optional)
    try:
        duty = duty_manager.start_duty(user, debtee=debtee)

    # failures
    except (UnfinishedDutyError,MaxDutyCountError) as e:
        return Response(
            {
                'success': False,
                'message': e.message,
                'now': "{:%m/%d/%Y %H:%M:%S}".format(timezone.localtime()),
            },
            status=status.HTTP_400_BAD_REQUEST 
        )

    # success
    serializer = DutySerializer(duty)
    return Response(
        {
            'success': True,
            'message': "Object %s created successfully" % duty,
            'payload': serializer.data,
            'now': "{:%m/%d/%Y %H:%M:%S}".format(timezone.localtime()),
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def duty_api_detail_view(request):
    user = request.user

    # preprocessing
    duty_manager.remove_finished_duties()

    if (user.duty_set.count() == 0) or (duty_manager.is_onduty(user) == False):
        return Response(
            {
                'success': False, 
                'message': "User's duty is not registered in manager",
                'now': "{:%m/%d/%Y %H:%M:%S}".format(timezone.localtime()),
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # success
    duties = duty_manager.get_duties_of(user)
    serializer = DutySerializer(duties, many=True)
    return Response(
        {
            'success': True,
            'message': "Duties sent. MAX_DUTY: %d" % DutyManager.MAX_DUTY,
            'payload': serializer.data,
            'now': "{:%m/%d/%Y %H:%M:%S}".format(timezone.localtime()),
        },
        status=status.HTTP_200_OK
    )
