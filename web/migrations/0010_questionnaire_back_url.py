# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_question_min_num_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='back_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
