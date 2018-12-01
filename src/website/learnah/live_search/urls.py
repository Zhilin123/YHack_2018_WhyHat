from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name="live_search"

urlpatterns = [
    # ex: /polls/
    # View
    path('', login_required(views.SearchView.as_view()), name='index'),
    # Ajax call, return json data
    #path('search_data/', login_required(views.SearchDataView.as_view()),
    #     name='search_data'),
    path('search_data/', views.SearchDataView.as_view(),
         name='search_data'),
]