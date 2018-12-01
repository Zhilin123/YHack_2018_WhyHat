
from django.contrib.auth.models import User
from data_manager.models import UserProfile

from django.contrib.auth import password_validation
from django import forms

def create_new_user(userName, userPass, userMail):

    if userName and userPass and userMail:
        if User.objects.filter(username = userName).count() > 0:
            return False, "This username is occupied."

        user = User.objects.create_user(username=userName,
                                        email=userMail)
        if user:
            # if the user is created
            try:
                # validate the password
                password_validation.validate_password(userPass, user)
            except forms.ValidationError as errors:
                err_message = "Password Invalid:"
                for error in errors:
                    err_message += "<br>" + error
                return False, err_message
            user.set_password(userPass)
            user.save()
            return True, "User is successfully created"
        else:
            # if user is not created
            return False, "User is not created."


def user_profile_edit(user):
    profile = UserProfile.objects.filter(user=user)
    if len(profile) == 0:
        # The profile doesn't exist
        # create a new user profile
        profile = UserProfile()
        profile.user = user

    # TODO: change profile content
    profile.save()

