# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-25 17:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_data', '0014_auto_20190825_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricing',
            name='variant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pricing', to='store_data.Variant'),
            preserve_default=False,
        ),
    ]
