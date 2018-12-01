# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import logout_then_login
from django.conf import settings
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect


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
