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
def update_user_interest_vector(user, video_url, video_title):
    profiles = UserProfile.objects.filter(user=user)
    if profiles.count() > 0:
        profile = profiles[0]
    else:
        return False

    if not profile.interest_vector: # no vector stored
        interest_vec = np.empty(Area.objects.all().count())
        interest_vec.fill(0)
        profile.update_interest_vector(interest_vec)
    else:
        interest_vec = profile.get_interest_vector()

    new_vector = vv.update_interest_vector(interest_vec, prev_video=(video_title, video_url))
    #print(interest_vec)
    #print(new_vector)

    profile.update_interest_vector(user.username, new_vector)
    #print(profile.get_interest_vector())


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
    #print(topic_list)

    if not profile.interest_vector: # no vector stored
        # call function
        interest_vec = np.empty(Area.objects.all().count())
        interest_vec.fill(0)
        profile.update_interest_vector(interest_vec)
    else:
        interest_vec = profile.get_interest_vector()

    #print(interest_vec)
    print("start calling")
    global vv
    rank = vv.get_ranked_video(topic_list, interest_vec, subject_weight=0.6, thresh=0, subject_mask_value=0)
    print("end calling")
    return rank[offset:offset+10]

