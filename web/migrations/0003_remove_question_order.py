# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20150304_0907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='order',
        ),
    ]
