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