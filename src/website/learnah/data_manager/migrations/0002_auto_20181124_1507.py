# Generated by Django 2.1.3 on 2018-11-24 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='subtitle',
        ),
        migrations.AddField(
            model_name='video',
            name='vector',
            field=models.FileField(null=True, upload_to='video_vector/'),
        ),
    ]
