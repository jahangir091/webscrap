# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-31 18:04
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store_data', '0008_auto_20190731_1741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='unit_price',
        ),
        migrations.AddField(
            model_name='variant',
            name='pricing',
            field=jsonfield.fields.JSONField(default=1),
            preserve_default=False,
        ),
    ]
