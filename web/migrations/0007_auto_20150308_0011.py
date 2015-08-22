# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20150308_0002'),
    ]

    operations = [
        migrations.RenameField(
            model_name='textanswer',
            old_name='selective_answer',
            new_name='selectiveanswer',
        ),
    ]
