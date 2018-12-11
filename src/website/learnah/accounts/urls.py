from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('login_signup/', views.LoginSignupView.as_view(), name='login_signup'),
    path('logout/', login_required(views.LogoutView.as_view()), name='logout')
]
