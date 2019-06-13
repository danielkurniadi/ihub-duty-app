from functools import wraps
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import status

def request_validator(validator):
	"""Decorator that will convert normal function into a decorator that can be used
	to validate request in api.py
	"""
	def __func(func):
		@wraps(func)
		def _func(request, *args, **kwargs):
			try:
				validator(request)
			except Exception as e:
				return Response(
					{
						'success': False,
						'message': e.message,
						'now': "{:%m/%d/%Y %H:%M:%S}".format(timezone.localtime())
					},
					status=status.HTTP_400_BAD_REQUEST
				)
			return func(request, *args, **kwargs)
		return _func
	return __func
