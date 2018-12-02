from django.contrib.auth.models import User
from data_manager.models import UserProfile, Subject, Unit, Topic, Area
from data_manager.VideoVectorizer import *
import numpy as np

vv = VideoVectorizer(folder='data_manager')
initialized = False
def initialize():
    print("initializing...")
    initialized = True

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

def obtain_recommend_videos(user, offset=0):
    if initialized == False:
        initialize()

    profiles = UserProfile.objects.filter(user=user)
    if profiles.count() > 0:
        profile = profiles[0]
    else:
        return False

    topics = profile.topics.all()
    topic_list = [topic.real_name for topic in topics]
    print(topic_list)

    if not profile.interest_vector: # no vector stored
        # call function
        interest_vec = np.empty(Area.objects.all().count())
        interest_vec.fill(0)
    else:
        interest_vec = profile.get_interest_vector()

    print(interest_vec)
    global vv
    rank = vv.get_ranked_video(topic_list, interest_vec, subject_weight=0.6, thresh=0, subject_mask_value=0)
    print(len(rank))
    return rank[offset:offset+10]

