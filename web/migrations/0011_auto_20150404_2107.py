# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_questionnaire_back_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertwitter',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserTwitter',
        ),
    ]
