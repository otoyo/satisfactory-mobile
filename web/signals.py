import re
from django.db.models.signals import pre_save
from django.dispatch import receiver
from web.models import Question


@receiver(pre_save, sender=Question)
def remove_num_answers_on_form_type_text(sender, instance, raw, using, **update_fields):
    if instance.form_type == Question.FORM_TYPE_TEXT:
        instance.min_num_answers = None
        instance.max_num_answers = None


@receiver(pre_save, sender=Question)
def adjust_max_num_answers(sender, instance, raw, using, **update_fields):
    if instance.max_num_answers and instance.max_num_answers and instance.max_num_answers < instance.min_num_answers:
        instance.max_num_answers = instance.min_num_answers
