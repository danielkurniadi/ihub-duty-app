from functools import wraps
from rest_framework.response import Response
from rest_framework.views import status

def manager_refresh(func):
    @wraps(func)
    def _func(self, *args, **kwargs):
        self.refresh() # from BaseManager interface
        return func(self, *args, **kwargs)
    return _func