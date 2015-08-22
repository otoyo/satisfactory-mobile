from django import forms
from web.models import Questionnaire, Question
from web.validators import validate_num_selectiveanswers


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    password = forms.CharField(min_length=8, max_length=24)


class PasswordForm(forms.Form):
    current_password = forms.CharField(min_length=8, max_length=24)
    password = forms.CharField(min_length=8, max_length=24)


class EmailForm(forms.Form):
    email = forms.EmailField(max_length=75)


class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
                'name',
                'content',
                'thanks_message',
                'back_url',
                'is_public',
                'start_at',
                'end_at',
                ]
        widgets = {
                'is_public': forms.RadioSelect,
                }


class QuestionFormForSelection(forms.Form):
    content = forms.CharField()
    form_type = forms.IntegerField(
            min_value=Question.FORM_TYPE_SELECTION,
            max_value=Question.FORM_TYPE_SELECTION
            )
    selectiveanswer = forms.CharField(
            validators=[validate_num_selectiveanswers]
            )
    min_num_answers = forms.IntegerField()
    max_num_answers = forms.IntegerField()


class QuestionFormForText(forms.Form):
    content = forms.CharField()
    form_type = forms.IntegerField(
            min_value=Question.FORM_TYPE_TEXT,
            max_value=Question.FORM_TYPE_TEXT
            )
