# Generated by Django 2.1.3 on 2018-11-24 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0002_auto_20181124_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, max_length=50)),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data_manager.Subject')),
            ],
        ),
        migrations.RemoveField(
            model_name='topic',
            name='parent_subject',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='parent_topic',
        ),
        migrations.AddField(
            model_name='topic',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data_manager.Unit'),
        ),
    ]
