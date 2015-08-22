from django.core.exceptions import ValidationError
from django.conf import settings

def validate_num_selectiveanswers(value):
    if len(value.rstrip().splitlines()) > settings.DEFAULT_QUESTION_LIMIT:
        raise ValidationError('Too many selectiveanswers.')
