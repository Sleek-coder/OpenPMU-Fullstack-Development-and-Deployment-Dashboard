# Generated by Django 4.2 on 2023-04-25 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PmuData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(blank=True, max_length=200, null=True)),
                ('time', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('frame', models.CharField(blank=True, max_length=200, null=True)),
                ('mag', models.FloatField(blank=True, max_length=200, null=True)),
                ('angle', models.FloatField(blank=True, max_length=200, null=True)),
                ('freq', models.FloatField(blank=True, max_length=500, null=True)),
                ('rocof', models.FloatField(blank=True, max_length=500, null=True)),
                ('channel', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'db_table': 'synchrophasor_data',
            },
        ),
    ]
