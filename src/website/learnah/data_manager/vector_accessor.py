from data_manager.models import Video
from django.contrib.auth.models import User
from django.core.files import File
import numpy as np


def upload_video_vector(target_video, myfile):
    # param: file:python file object
    target_video.vector.save("vector.npx", myfile)
    target_video.save()


def get_video_vector(target_video):
    # return: numpy array stored in this video
    f = target_video.vector.open()
    return np.load(f)