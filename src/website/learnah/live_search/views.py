import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from data_manager.models import UserProfile, Subject, Unit, Topic, Area
from django.contrib.auth.models import User
from django.core.files import File
from accounts.user_registration import create_new_user

class SearchView(TemplateView):
    template_name = 'live_search/index.html'

    def get(self, request, *args, **kwargs):
        params = dict()

        params['current_user'] = request.user

        return self.render_to_response(params)

class SearchDataView(TemplateView):
    # API call processing
    template_name = 'live_search/index.html'

    def get(self, request, *args, **kwargs):
        print (request)
        input = request.GET['input']
        strs = input.split(" ")
        data = {"videos":[]}
        for item in strs:
            if item != "":
                data['videos'].append({
                    "title":item,
                    "description":str("description of " + item),
                    "url": str("www.youtube.com/" + "watch?v=xHYYWFUTLZE"), #toydata
                })
        print (data)
        return JsonResponse({
            'data': data,
        })

class AreaTopicDataView(TemplateView):
    # API call processing
    template_name = 'live_search/index.html'
    '''
    
    This api returns all the areas string and topics string
    GET:
    RETURN:
    {
        areas:[area_1, area_2, ....],
        topics:{
            "subject_1":{
                "unit_1":{
                    topic_1, topic_2, ...
                }
            },
            "subject_2":{...},
            ....,
    }
    '''
    def get(self, request, *args, **kwargs):
        data = []
        topics_data = {}
        for topic in Topic.objects.all():
            unit = topic.unit
            subject = unit.subject
            topics_data.setdefault(subject.name, {}).setdefault(unit.name, []).append(topic.name)

        return JsonResponse({
            'areas': [x.name for x in Area.objects.all()],
            'topics': topics_data,
            'msg': "Return Successfully",
        })

class UserProfileDataView(TemplateView):
    # API call processing
    template_name = 'live_search/index.html'
    '''
    This api returns the current user choice of topics and areas
    
    GET:
    username: string
    RETURN:
    {
        areas:[area_1, area_2, ....],
        topics:[topic_1, topic_2, ...],
    }
    '''
    def get(self, request, *args, **kwargs):
        data = []
        username = request.GET['username']
        res, err_message = create_new_user(username, 'nopassword', 'nomail@gmail.com')
        try:
            user = User.objects.get(username=username)

            profiles = UserProfile.objects.filter(user=user)
            if profiles.count() > 0:
                profile = profiles[0]
            else:
                profile = UserProfile()
                profile.user = user
                profile.save()

            return JsonResponse({
                'areas': [x.name for x in profile.areas.all()],
                'topics': [x.name for x in profile.topics.all()],
                'msg': "Return Successfully",
            })
        except:
            return JsonResponse({
                'areas': [],
                'topics': [],
                'msg': "Internal Server Error",
            })





class RecommendDataView(TemplateView):
    # API call processing
    template_name = 'live_search/index.html'
    '''
    GET:
    username: string
    areas: list of strings
    topics: list of strings
    RETURN:
    {
        [
             {url of video 1 <string>: title of video 1 <string>},
             {url of video 2 <string>: title of video 2 <string>},
             ...
        ]
    }
    '''
    def get(self, request, *args, **kwargs):
        data = []
        username = request.GET['username']
        areas = request.GET['areas']
        topics = request.GET['topics']

        res, err_message = create_new_user(username, 'nopassword', 'nomail@gmail.com')
        try:
            user = User.objects.get(username=username)

            profiles = UserProfile.objects.filter(user=user)
            if profiles.count() > 0:
                profile = profiles[0]
            else:
                profile = UserProfile()
                profile.user = user
                profile.save()

            for area_name in areas:
                area = Area.objects.get(name=area_name)
                profile.areas.add(area)

            for topic_name in topics:
                topic = Topic.objects.get(name=topic_name)
                profile.topics.add(topic)

            return JsonResponse({
                'data': data,
                'msg': "Return Successfully",
            })
        except:
            return JsonResponse({
                'data': [],
                'msg': "Internal Server Error",
            })