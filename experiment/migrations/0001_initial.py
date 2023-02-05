# Generated by Django 4.1.5 on 2023-02-05 03:43

from django.db import migrations, models
import django.db.models.deletion
import experiment.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experiments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='user id')),
                ('run_name', models.CharField(max_length=128, verbose_name='experiment name')),
                ('file_name', models.CharField(max_length=128, verbose_name='file')),
                ('state', models.CharField(blank=True, choices=[('finished', 'finished'), ('pending', 'pending'), ('failed', 'failed')], max_length=200, null=True, verbose_name='state')),
                ('odm', models.CharField(blank=True, choices=[('ABOD', 'Angle-based Outlier Detector'), ('KNN', 'k-Nearest Neighbors Detector')], max_length=128, null=True, verbose_name='odm')),
                ('operation', models.CharField(blank=True, max_length=128, null=True, verbose_name='logical formula')),
                ('auxiliary_file_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='file')),
                ('columns', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FinishedExperiments',
            fields=[
                ('experiments_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='experiment.experiments')),
                ('result_path', models.CharField(max_length=128, verbose_name='result path')),
                ('start_time', models.TimeField(auto_now_add=True, verbose_name='start time')),
                ('duration', models.IntegerField(verbose_name='run duration')),
            ],
            bases=('experiment.experiments',),
        ),
        migrations.CreateModel(
            name='PendingExperiments',
            fields=[
                ('experiments_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='experiment.experiments')),
                ('main_file', models.FileField(upload_to=experiment.models.user_directory_path, verbose_name='main file path')),
                ('generated_file', models.FileField(upload_to=experiment.models.user_directory_path, verbose_name='generated file path')),
                ('ground_truth', models.FileField(upload_to=experiment.models.user_directory_path, verbose_name='ground truth path')),
            ],
            bases=('experiment.experiments',),
        ),
    ]
