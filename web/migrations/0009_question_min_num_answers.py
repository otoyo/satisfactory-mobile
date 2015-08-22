# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_usertwitter'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='min_num_answers',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
