# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='form_type',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='max_num_answers',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=True,
        ),
    ]
