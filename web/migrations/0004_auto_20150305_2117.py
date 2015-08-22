# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_remove_question_order'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='question',
            order_with_respect_to='questionnaire',
        ),
        migrations.AlterOrderWithRespectTo(
            name='selectiveanswer',
            order_with_respect_to='question',
        ),
    ]
