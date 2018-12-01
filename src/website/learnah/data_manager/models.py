from django.db import models
from django.contrib.auth.models import User
import numpy as np

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topic_vector = models.FileField(upload_to='topic_vector/', null=True)

    def upload_topic_vector(self, myfile):
        # param: file:python file object
        self.topic_vector.save("topic_vector.npx", myfile)
        self.save()

    def get_topic_vector(self):
        # return: numpy array stored in this video
        f = self.topic_vector.open()
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
    description = models.CharField(max_length=255, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, null=True)
    def __str__(self):
        string = "unit:"+ self.unit.name + "name: " + self.name + "\n" + "des: " + self.description
        return string


class Video(models.Model):
    title = models.CharField(max_length=30)
    url = models.URLField()
    vector = models.FileField(upload_to='video_vector/', null=True)

    def upload_video_vector(self, myfile):
        # param: file:python file object
        self.vector.save("vector.npx", myfile)
        self.save()

    def get_video_vector(self):
        # return: numpy array stored in this video
        f = self.vector.open()
        return np.load(f)


class VideoHistory(models.Model):
    video = models.ForeignKey('Video', on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Area(models.Model):
    name = models.CharField(max_length=30)