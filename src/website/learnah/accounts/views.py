# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import logout_then_login
from django.conf import settings
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from data_manager.models import UserProfile
from accounts.user_registration import create_new_user
from django.contrib.auth.models import User

class LoginView(TemplateView):
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        params = dict()
        return self.render_to_response(params)

    def post(self, request):
        username = request.POST["username"].strip()
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

            # persistent cookie
            # set the login expiration time
            expires = datetime.now()
            expires += timedelta(
                days=settings.PERSISTENT_COOKIE_EXPIRES)
            response.set_cookie(settings.SESSION_COOKIE_NAME, expires=expires)

            return response
        else:
            # if the user is not authenticated.
            params = dict()
            params['error'] = 'Email address or Password invalid'
            return self.render_to_response(params)


class LogoutView(TemplateView):
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    def post(self, request):
        return logout_then_login(request)



class LoginSignupView(TemplateView):
    '''
    GET:
    username string
    RETURN:
    {
        'msg':'Login Successfully'/'Signup Successfully'/'Fail'
    }
    '''
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        username = request.GET['username']

        res, err_message = create_new_user(username, 'nopassword', 'nomail@gmail.com')
        try:
            user = User.objects.get(username=username)

            profiles = UserProfile.objects.filter(user=user)
            if profiles.count() > 0:
                return JsonResponse({
                    'msg': "Login Successfully",
                })
            else:
                return JsonResponse({
                    'msg': "Signup Successfully",
                })
        except:
            return JsonResponse({
                'msg': "Fail",
            })