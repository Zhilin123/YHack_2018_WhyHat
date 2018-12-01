from django.contrib.auth.models import User
from data_manager.models import UserProfile, Subject, Unit, Topic

'''
Here is the interface between backend server and algorithm
'''
def update_user_interest_vector(user, video_url):
    profiles = UserProfile.objects.filter(user=user)
    if profiles.count() > 0:
        profile = profiles[0]
    else:
        return False

    if not profile.interest_vector: # no vector stored
        # call function
        pass
        # (np.array([0*300]), video_url)
    else:
        # there's a vector
        pass
        # (profile.get_interest_vector(), video_url)
    # new_vector = ...
    #
    # profile.update_interest_vector(user.username, new_vector)

def obtain_recommend_videos(user):
    profiles = UserProfile.objects.filter(user=user)
    if profiles.count() > 0:
        profile = profiles[0]
    else:
        return False

    topics = profile.topics.all()
    topic_list = [topic.name for topic in topics]
    print(topic_list)

    if not profile.interest_vector: # no vector stored
        # call function
        pass
        # (np.array([0*300]), topic_list)
    else:
        # there's a vector
        pass
        # (profile.get_interest_vector(), topic_list)
