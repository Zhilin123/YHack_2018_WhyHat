from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "home"

urlpatterns = [
    # ex: /polls/
    path('', login_required(views.HomeView.as_view()), name='index'),
]