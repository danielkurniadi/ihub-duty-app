from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from users.forms import SignUpForm


########################################
# Login
########################################

def redirect_login(request):
    """Redirect users to login page if not logged in.
        If logged in, allow access and go to their profile page.
    """
    # GET
    if request.method == 'GET':
        # same as permission(IsAuthenticated)
        if request.user.is_authenticated:
            return redirect('users:home')
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


########################################
# User pages
########################################

class HomeView(LoginRequiredMixin, DetailView):
    """Render user home page. 
    """
    template_name = 'home.html'

    def get_object(self, queryset=None):
        return self.request.user


########################################
# Sign up
########################################

def signup(request):
    """Render forms and page for sign up and create new user 
        with basic permission level.
    """
    # POST
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # create, authenticate, and login user
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, email=user.email, password=raw_password)
            if user:
                # successful authentication
                login(request, user)
                return redirect('users:home')

    # GET (assumed)
    else:
        form = SignUpForm()

    # signup fail or first try signup
    return render(request, 'signup.html', {'form': form})
