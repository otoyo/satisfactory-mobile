import hashlib, logging, time
from django.db import models
from django.db.models import F, Sum
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
from web.utils import CSVDumper

logger = logging.getLogger(__name__)


class UrlKey(models.Model):
    KEY_LEN = 8
    RETRY_COUNT = 10

    val = models.SlugField(unique=True)

    @classmethod
    def register(self, seed):
        for i in range(self.RETRY_COUNT):
            try:
                urlkey = UrlKey(val=hashlib.sha512(self._salt(seed)).hexdigest()[0:self.KEY_LEN])
                urlkey.validate_unique()
            except ValidationError as e:
                logger.warning('Conflict urlkey.val, val: {0}'.format(urlkey.val))
                if i == self.RETRY_COUNT - 1:
                    raise
            else:
                urlkey.save()
                return urlkey

    @classmethod
    def _salt(self, seed):
        return (str(seed) + str(time.time())).encode('utf-8')

class Questionnaire(models.Model):

    class Meta():
        index_together = [['start_at', 'end_at']]

    user = models.ForeignKey(User)
    urlkey = models.ForeignKey(UrlKey)
    name = models.CharField(max_length=70)
    content = models.TextField()
    thanks_message = models.TextField()
    back_url = models.URLField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_urlkey(self):
        self.urlkey = UrlKey.register(self.user.id)
        return self

    @classmethod
    def listup_by_user_id(self, user_id):
        list = {'private': [], 'before_start': [], 'open': [], 'after_end': []}
        now = timezone.now()
        questionnaires = Questionnaire.objects.filter(user_id=user_id)
        for questionnaire in questionnaires:
            if questionnaire.is_public:
                if questionnaire.is_before_start(now):
                    list['before_start'].append(questionnaire)
                elif questionnaire.is_after_end(now):
                    list['after_end'].append(questionnaire)
                else:
                    list['open'].append(questionnaire)
            else:
                list['private'].append(questionnaire)
        return list

    def is_before_start(self, t=timezone.now()):
        return self.start_at is not None and t < self.start_at

    def is_after_end(self, t=timezone.now()):
        return self.end_at is not None and t > self.end_at

    def is_open(self):
        return self.is_public and not self.is_before_start() and not self.is_after_end()

    def validate(self, post_data):
        errors = {}
        for question in self.question_set.all():
            if question.is_selection_form_type():
                if question.is_radio():
                    selectiveanswer_set = SelectiveAnswer.objects.filter(
                            id=post_data['question_{0}'.format(question.id)],
                            question_id=question.id,
                            )
                    if not selectiveanswer_set.exists():
                        raise ValidationError(
                                _('Invalid selectiveanswer id'),
                                code='invalid selectiveanswer id'
                                )
                else:
                    is_valid, selectiveanswer_ids = question.validate_num_answers(post_data)
                    if is_valid:
                        for selectiveanswer_id in selectiveanswer_ids:
                            selectiveanswer_set = SelectiveAnswer.objects.filter(
                                    id=selectiveanswer_id,
                                    question_id=question.id,
                                    )
                            if not selectiveanswer_set.exists():
                                raise ValidationError(
                                        _('Invalid selectiveanswer id'),
                                        code='invalid selectiveanswer id'
                                        )
                    else:
                        errors = dict(
                                {'question_{0}'.format(question.id): 'invalid num'},
                                **errors
                                )
            else:
                if not 'question_{0}'.format(question.id) in post_data:
                    raise ValidationError(
                            _('Invalid question id'), code='invalid question id')
        return errors

    def accept(self, post_data):
        for question in self.question_set.all():
            if question.is_selection_form_type():
                if question.is_radio():
                    selectiveanswer = SelectiveAnswer.objects.get(
                            pk=post_data['question_{0}'.format(question.id)])
                    selectiveanswer.num = F('num') + 1
                    selectiveanswer.save()
                else:
                    for selectiveanswer in question.selectiveanswer_set.all():
                        name = 'question_{0}_selectiveanswer_{1}'.format(
                                question.id, selectiveanswer.id)
                        if name in post_data:
                            selectiveanswer = SelectiveAnswer.objects.get(
                                    pk=selectiveanswer.id)
                            selectiveanswer.num = F('num') + 1
                            selectiveanswer.save()
            else:
                if (post_data['question_{0}'.format(question.id)] != ''):
                    question.textanswer_set.create(
                            content=post_data['question_{0}'.format(question.id)])
        return None

    def dump_as_csv(self, encoding='sjis'):
        rows = []
        for question in self.question_set.all():
            rows.append([question.content])
            if question.is_selection_form_type():
                rows.append([None, 'Answer', 'Percentage', 'Number'])
                for selectiveanswer in question.selectiveanswer_set.all():
                    rows.append([
                        None,
                        selectiveanswer.content,
                        selectiveanswer.percentage(),
                        selectiveanswer.num
                        ])
            else:
                rows.append([None, 'Answer'])
                for textanswer in question.textanswer_set.all():
                    rows.append([None, textanswer.content])
        return CSVDumper.dump(rows, encoding)


class Question(models.Model):
    FORM_TYPE_SELECTION = 1
    FORM_TYPE_TEXT = 2

    class Meta:
        order_with_respect_to = 'questionnaire'

    questionnaire = models.ForeignKey(Questionnaire)
    content = models.TextField()
    form_type = models.PositiveSmallIntegerField(
            default=1,
            validators=[RegexValidator(regex='^[12]$')]
            )
    max_num_answers = models.PositiveSmallIntegerField(null=True, blank=True)
    min_num_answers = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_selection_form_type(self):
        return self.form_type == self.FORM_TYPE_SELECTION

    def is_radio(self):
        return self.min_num_answers == 1 and self.max_num_answers == 1

    def validate_num_answers(self, post_data):
        count = 0
        selectiveanswer_ids = []
        for selectiveanswer in self.selectiveanswer_set.all():
            name = 'question_{0}_selectiveanswer_{1}'.format(
                    self.id, selectiveanswer.id)
            if name in post_data:
                count = count + 1
                selectiveanswer_ids.append(selectiveanswer.id)
        is_valid = self.min_num_answers <= count <= self.max_num_answers
        return [is_valid, selectiveanswer_ids]

    def sum_selectiveanswer_num(self):
        return self.selectiveanswer_set.all().aggregate(Sum('num'))['num__sum']

    def limit_textanswers(self, limit=5, order='desc'):
        column = '-id' if order == 'desc' else 'id'
        return self.textanswer_set.order_by(column)[:limit]


class SelectiveAnswer(models.Model):

    class Meta:
        order_with_respect_to = 'question'

    question = models.ForeignKey(Question)
    content = models.TextField()
    num = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def percentage(self, digit=2):
        if self.question.sum_selectiveanswer_num() == 0:
            return None
        return int(self.num * 10 ** (digit + 2) / self.question.sum_selectiveanswer_num()) / 100.0


class TextAnswer(models.Model):
    question = models.ForeignKey(Question)
    selectiveanswer = models.ForeignKey(SelectiveAnswer, null=True, blank=True)
    content = models.TextField() # Records must be having content
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def paginate(self, question_id, max_id=None, limit=20):
        queryset = self.objects.order_by('-id')
        if max_id:
            queryset = queryset.filter(id__lte=max_id)

        textanswers = list(queryset.all()[:limit + 1])

        next_max_id = None
        if (len(textanswers) > limit):
            next_max_id = textanswers.pop().id

        return {'textanswers': textanswers, 'next_max_id': next_max_id}


class Help(models.Model):
    title = models.CharField(max_length=140)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
