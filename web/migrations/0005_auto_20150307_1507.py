# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20150305_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='max_num_answers',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
