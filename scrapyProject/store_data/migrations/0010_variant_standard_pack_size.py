# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-31 18:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_data', '0009_auto_20190731_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='standard_pack_size',
            field=models.IntegerField(blank=True, default=0, help_text='number of items in a pack'),
        ),
    ]
