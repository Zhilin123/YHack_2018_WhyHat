import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from data_manager.models import UserProfile, Subject, Unit, Topic, Video
from django.contrib.auth.models import User
from django.core.files import File

from data_manager.vector_accessor import upload_video_vector, get_video_vector
from data_manager.data_import import import_chemistry_topics, import_physics_topics, import_topics


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):

        Subject.objects.all().delete()
        Unit.objects.all().delete()
        Topic.objects.all().delete()

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
        #print(Video.objects.all())
        #test_video = Video.objects.all()[0]

        #print(test_video.get_video_vector())

        # re-import the topics and units
        if Topic.objects.all().count() == 0:
            Unit.objects.all().delete()
            Topic.objects.all().delete()
            #import_chemistry_topics()
            #import_physics_topics()
            import_topics()

        #print(Unit.objects.filter(subject__name="Chemistry"))
        #print(Unit.objects.filter(subject__name="Physics"))
        #print(Unit.objects.filter(subject__name="Biology"))

        params['current_user'] = request.user
        params["input_param"] = str("total number of records in topics: " + str(Topic.objects.all().count()))
        return self.render_to_response(params)