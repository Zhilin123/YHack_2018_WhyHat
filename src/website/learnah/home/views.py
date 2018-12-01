import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from data_manager.models import UserProfile, Subject, Unit, Topic
from django.contrib.auth.models import User
from django.core.files import File
from data_manager.backend_interface import obtain_recommend_videos
from data_manager.data_import import import_chemistry_topics, import_physics_topics, import_topics
from accounts.user_registration import create_new_user

class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):
        params = dict()
        subjects = Subject.objects.all()

        if len(subjects) == 0:
            subjects.delete()
            for x in ["Physics","Chemistry","Biology"]:
                subject = Subject()
                subject.name = x
                subject.description = x + "for test"
                subject.save()

        '''
        Video.objects.all().delete()
        
        f = open('data_manager/temp.npx', 'rb')
        myfile = File(f)
        
        test_video = Video()
        test_video.name = "test video"
        test_video.url = "www.google.com/testvideo"
        test_video.save()
        test_video.vector.save("temp.npx", myfile)
        test_video.save()
        '''

        # re-import the topics and units
        if Topic.objects.all().count() == 0:
            Unit.objects.all().delete()
            Topic.objects.all().delete()
            #import_chemistry_topics()
            #import_physics_topics()
            import_topics()

        print(Unit.objects.filter(subject__name="Chemistry"))
        print(Unit.objects.filter(subject__name="Physics"))
        print(Unit.objects.filter(subject__name="Biology"))


        profiles = UserProfile.objects.filter(user=request.user)
        if profiles.count() == 0:
            profile = UserProfile()
            profile.user = request.user
            profile.save()
        else:
            profile = profiles[0]
        profile.update_interest_vector(request.user.username, np.array([5,6,7,8]))
        print(profile.get_interest_vector())
        topics = Topic.objects.filter(unit__subject__name="Physics")
        print(topics)
        for topic in topics:
            profile.topics.add(topic)

        #print(profile.topics.all().count())
        #obtain_recommend_videos(request.user)
        params['current_user'] = request.user

        #res, err_message = create_new_user("test_user","test_password", "test_mail@gmail.com")
        #print(res, err_message)

        params["input_param"] = str("total number of records in topics: " + str(Topic.objects.all().count()) + str(list(Topic.objects.all())))
        return self.render_to_response(params)