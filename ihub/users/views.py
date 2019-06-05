from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate


def redirect_login(request):
    """Redirect users to login page if not logged in.
        If logged in, allow access and go to their profile page.
    """
    # GET
    if request.method == 'GET':
        # @permission(IsAuthenticated)
        if request.user.is_authenticated:
            return redirect('users:profile')
        return redirect('/accounts/login/')

    # ERROR for other method
    else:
        return Response(
            {
                'success': False,
                'message': "Cannot process this endpoint with %s request method"
                    % (request.method),
            }, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class HomeView(DetailView):
    """Render user profile page. 
    """
    template_name = 'home.html'

    def get_object(self, queryset=None):
        return self.request.user



