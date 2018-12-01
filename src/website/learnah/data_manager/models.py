from django.db import models
from django.contrib.auth.models import User
import numpy as np
from django.core.files import File
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topics = models.ManyToManyField('Topic')
    areas = models.ManyToManyField('Area')

    interest_vector = models.FileField(upload_to='interest_vector/', null=True)
    def update_interest_vector(self, prefix, vector):
        # param: file:python file object
        np.save('temp.npy', vector)
        myfile = File(open('temp.npy', 'rb'))
        self.interest_vector.save(prefix + "_interest_vector.npy", myfile)
        self.save()

    def get_interest_vector(self):
        # return: numpy array stored in this video
        f = self.interest_vector.open()
        return np.load(f)


class Subject(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        string = "name: " + self.name + "\n" + "des: " + self.description
        return string


class Unit(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True)
    def __str__(self):
        string = "subject:"+ self.subject.name + " name: " + self.name + "\n" + "des: " + self.description
        return string


class Topic(models.Model):
    name = models.CharField(max_length=255)
    real_name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True)
    def __str__(self):
        string = "unit:"+ self.unit.name + " name: " + self.name
        return string


class VideoHistory(models.Model):
    video_url = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Area(models.Model):
    name = models.CharField(max_length=30)