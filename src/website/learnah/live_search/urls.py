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
    path('recommend_data/', views.RecommendDataView.as_view(),
         name='recommend_data'),
    path('topicarea_data/', views.AreaTopicDataView.as_view(),
         name='topicarea_data'),
    path('profile_data/', views.UserProfileDataView.as_view(),
         name="profile_data"),
    path('profile_update/', views.UserProfileUpdateView.as_view(),
         name="profile_update"),
    path('video_watch/', views.VideoWatchView.as_view(),
         name="video_watch"),
]