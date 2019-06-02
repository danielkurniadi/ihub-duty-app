from django.urls import path, include
from django.contrib.auth.views import LoginView
from .views import HomeView, signup

app_name = 'users'

urlpatterns = [
    path('profile/', HomeView.as_view(), name='home'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(
            template_name='login.html', 
            redirect_authenticated_user=True), 
        name='login'),
]
