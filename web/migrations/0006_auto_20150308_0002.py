# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20150307_1507'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionnaire',
            old_name='url_key',
            new_name='urlkey',
        ),
        migrations.AlterField(
            model_name='question',
            name='form_type',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.RegexValidator(regex='^[12]$')]),
            preserve_default=True,
        ),
    ]
