# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 18:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cognito', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='CognitoUser',
        ),
    ]
