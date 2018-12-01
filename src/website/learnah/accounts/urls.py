from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', login_required(views.LogoutView.as_view()), name='logout')
]
