import logging
from datetime import timedelta
from unittest.mock import MagicMock
from django.db.models import F
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import Client
from web.models import *
from web.utils import CSVDumper

class ViewTests(TestCase):
    fixtures = ['user.json', 'urlkey.json', 'questionnaire.json', 'question.json', 'selectiveanswer.json']
    client = Client()

    def setUp(self):
        self.client.login(username='satisfactory.mobile', password='satisfactory.mobile')

    def test_signup_success(self):
        count = User.objects.count()
        res = Client().post('/signup', {
            'username': 'satisfactory',
            'email': 'satisfactory@example.com',
            'password': 'satisfactory.mobile',
            })
        self.assertEqual(User.objects.count() - count, 1)
        self.assertEqual(res.status_code, 200)

    def test_signup_failure(self):
        count = User.objects.count()
        res = Client().post('/signup', {
            'username': 'satisfactory.mobile',
            'email': 'satisfactory-mobile@example.com',
            'password': 'satisfactory.mobile',
            })
        self.assertEqual(User.objects.count() - count, 0)
        self.assertEqual(res.status_code, 200)

    def test_login_success(self):
        res = Client().post('/login', {
            'username': 'satisfactory.mobile', 'password': 'satisfactory.mobile'})
        self.assertEqual(res.status_code, 302)

    def test_login_failure(self):
        res = Client().post('/login', {'username': '', 'password': ''})
        self.assertEqual(res.status_code, 200)

    def test_logout(self):
        res = self.client.get('/logout')
        self.assertEqual(res.status_code, 302)

    def test_resign(self):
        res = self.client.post('/resign', {})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.get(pk=1).is_active)
        self.assertFalse(Questionnaire.objects.get(pk=2).is_public)

    def test_account_email_update(self):
        res = self.client.post('/account/email/update', {
            'email': 'satisfactory-mobile@example.com',
            })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(User.objects.get(pk=1).email, 'satisfactory-mobile@example.com')

    def test_account_password_update(self):
        res = self.client.post('/account/password/update', {
            'current_password': 'satisfactory.mobile',
            'password': 'satisfactory',
            })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.get(pk=1).check_password('satisfactory'))

    def test_questionnaire_index_without_login_session(self):
        res = Client().get('/questionnaire')
        self.assertEqual(res.status_code, 302)

    def test_questionnaire_create(self):
        count = Questionnaire.objects.count()
        res = self.client.post('/questionnaire/create', {
            'name': 'some questionnaire',
            'content': 'some content',
            'thanks_message': 'some message',
            'back_url': 'http://alpacat.com',
            'is_public': '0',
            'start_at': '2015-02-01',
            'end_at': '2015-02-28',
            })
        self.assertEqual(Questionnaire.objects.count() - count, 1)
        self.assertEqual(res.status_code, 302)

    def test_questionnaire_update(self):
        questionnaire = Questionnaire.objects.first()
        res = self.client.post('/questionnaire/{0}/update'.format(questionnaire.id), {
            'name': 'some questionnaire',
            'content': 'some content',
            'thanks_message': 'some message',
            'back_url': 'http://alpacat.com',
            'is_public': '0',
            'start_at': '2015-02-01',
            'end_at': '2015-02-28',
            })
        self.assertEqual(Questionnaire.objects.first().name, 'some questionnaire')
        self.assertEqual(res.status_code, 302)

    def test_questionnaire_delete(self):
        count = Questionnaire.objects.count()
        questionnaire = Questionnaire.objects.first()
        res = self.client.post('/questionnaire/{0}/delete'.format(questionnaire.id))
        self.assertEqual(count - Questionnaire.objects.count(), 1)
        self.assertEqual(questionnaire.question_set.count(), 0)
        self.assertEqual(res.status_code, 302)

    def test_question_create_as_textanswer(self):
        questionnaire = Questionnaire.objects.first()
        count = questionnaire.question_set.count()
        res = self.client.post('/questionnaire/{0}/question/create'.format(questionnaire.id), {
            'content': 'some content',
            'form_type': str(Question.FORM_TYPE_TEXT),
            'selectiveanswer': '',
            'min_num_answers': '1',
            'max_num_answers': '1',
            })
        self.assertEqual(questionnaire.question_set.count() - count, 1)
        self.assertEqual(res.status_code, 302)

    def test_question_create_as_selectiveanswer(self):
        questionnaire = Questionnaire.objects.first()
        count = questionnaire.question_set.count()
        res = self.client.post('/questionnaire/{0}/question/create'.format(questionnaire.id), {
            'content': 'some content',
            'form_type': str(Question.FORM_TYPE_SELECTION),
            'selectiveanswer': 'selection1\nselection2\nselection3',
            'min_num_answers': '1',
            'max_num_answers': '1',
            })
        self.assertEqual(questionnaire.question_set.count() - count, 1)
        self.assertEqual(questionnaire.question_set.last().selectiveanswer_set.count(), 3)
        self.assertEqual(res.status_code, 302)

    def test_question_create_as_selectiveanswer_with_invalid_num_answers(self):
        questionnaire = Questionnaire.objects.first()
        count = questionnaire.question_set.count()
        res = self.client.post('/questionnaire/{0}/question/create'.format(questionnaire.id), {
            'content': 'some content',
            'form_type': str(Question.FORM_TYPE_SELECTION),
            'selectiveanswer': 'selection1\nselection2\nselection3',
            'min_num_answers': '12',
            'max_num_answers': '12',
            })
        self.assertEqual(questionnaire.question_set.last().min_num_answers, 3)
        self.assertEqual(questionnaire.question_set.last().max_num_answers, 3)

    def test_question_delete(self):
        questionnaire = Questionnaire.objects.first()
        question = questionnaire.question_set.first()
        count = questionnaire.question_set.count()
        res = self.client.post('/questionnaire/{0}/question/{1}/delete'.format(questionnaire.id, question.id))
        self.assertEqual(count - questionnaire.question_set.count(), 1)
        self.assertEqual(SelectiveAnswer.objects.filter(question_id=question.id).count() + TextAnswer.objects.filter(question_id=question.id).count(), 0)
        self.assertEqual(res.status_code, 302)

    def test_question_reorder(self):
        questionnaire = Questionnaire.objects.first()
        question_ids = questionnaire.get_question_order()
        reordered_question_ids = [question_ids.pop()] + question_ids
        res = self.client.post('/questionnaire/{0}/question/reorder'.format(questionnaire.id), {
            'question_ids': ','.join([str(id) for id in reordered_question_ids]),
            })
        self.assertListEqual(questionnaire.get_question_order(), reordered_question_ids)
        self.assertEqual(res.status_code, 302)

    def test_textanswer_index_with_textanswer(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        question = Question.objects.get(pk=3)
        res = self.client.get('/questionnaire/{0}/question/{1}/textanswer'.format(questionnaire.id, question.id))
        self.assertEqual(res.status_code, 200)

    def test_textanswer_index_without_textanswer(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        question = Question.objects.get(pk=1)
        res = self.client.get('/questionnaire/{0}/question/{1}/textanswer'.format(questionnaire.id, question.id))
        self.assertEqual(res.status_code, 404)

    def test_resource_csv(self):
        post_data = {
                'question_1': "1",
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_3': "some content",
                }
        Questionnaire.objects.get(pk=1).accept(post_data)

        questionnaire = Questionnaire.objects.get(pk=1)
        res = self.client.get('/resource/utf8/questionnaire{0}.csv'.format(questionnaire.id))
        self.assertEqual(res.status_code, 200)

        rows = []
        for line in res.content.decode('utf8').splitlines():
            rows.append(line.rstrip().split(','))
        self.assertListEqual(rows[0], ['"1st question"'])
        self.assertListEqual(rows[1], ['', '"Answer"', '"Percentage"', '"Number"'])
        self.assertListEqual(rows[2], ['', '"1st answer"', '"100.0"', '1'])
        self.assertListEqual(rows[3], ['', '"2nd answer"', '"0.0"', '0'])
        self.assertListEqual(rows[4], ['"2nd question"'])
        self.assertListEqual(rows[5], ['', '"Answer"', '"Percentage"', '"Number"'])
        self.assertListEqual(rows[6], ['', '"1st answer"', '"50.0"', '1'])
        self.assertListEqual(rows[7], ['', '"2nd answer"', '"50.0"', '1'])
        self.assertListEqual(rows[8], ['', '"3rd answer"', '"0.0"', '0'])
        self.assertListEqual(rows[9], ['"3rd question"'])
        self.assertListEqual(rows[10], ['', '"Answer"'])
        self.assertListEqual(rows[11], ['', '"some content"'])

    def test_form_questionnaire_not_found(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        res = self.client.post('/-/{0}'.format(questionnaire.urlkey.val))
        self.assertEqual(res.status_code, 404)

    def test_form_submit(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        questionnaire.is_public = True
        questionnaire.save()
        res = self.client.post('/-/{0}'.format(questionnaire.urlkey.val), {
            'question_1': "1",
            'question_2_selectiveanswer_3': "1",
            'question_2_selectiveanswer_4': "1",
            'question_3': "some content",
            })
        self.assertEqual(SelectiveAnswer.objects.get(pk=1).num, 1)
        self.assertEqual(SelectiveAnswer.objects.get(pk=3).num, 1)
        self.assertEqual(SelectiveAnswer.objects.get(pk=4).num, 1)
        self.assertEqual(TextAnswer.objects.count(), 1)
        self.assertEqual(res.status_code, 200)


class UrlKeyTests(TestCase):

    def test_register_logs_and_raises(self):
        UrlKey._salt = MagicMock()
        UrlKey._salt.return_value = 'frozen_salt'.encode('utf-8')
        logger = logging.getLogger('web.models')
        logger.warning = MagicMock()

        with self.assertRaises(ValidationError):
            UrlKey.register(1)
            UrlKey.register(1)

    def test_register_returns_urlkey(self):
        urlkey = UrlKey.register(1)
        self.assertTrue(isinstance(urlkey, UrlKey))
        self.assertEqual(len(urlkey.val), UrlKey.KEY_LEN)


class QuestionnaireTests(TestCase):
    fixtures = ['user.json', 'urlkey.json', 'questionnaire.json', 'question.json', 'selectiveanswer.json']

    def setUp(self):
        before_start = Questionnaire.objects.get(pk=2)
        before_start.start_at = timezone.now() + timedelta(days=1)
        before_start.save()

        open = Questionnaire.objects.get(pk=3)
        open.start_at = timezone.now() - timedelta(days=1)
        open.end_at = timezone.now() + timedelta(days=1)
        open.save()

        after_end = Questionnaire.objects.get(pk=4)
        after_end.end_at = timezone.now() - timedelta(days=1)
        after_end.save()

    def test_set_urlkey(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        questionnaire.set_urlkey()
        self.assertTrue(isinstance(questionnaire.urlkey, UrlKey))

    def test_listup_by_user_id(self):
        list = Questionnaire.listup_by_user_id(1)
        self.assertEqual(len(list['private']), 1)
        self.assertEqual(len(list['before_start']), 1)
        self.assertEqual(len(list['open']), 1)
        self.assertEqual(len(list['after_end']), 1)

    def test_is_before_start(self):
        self.assertTrue(Questionnaire.objects.get(pk=2).is_before_start())
        self.assertFalse(Questionnaire.objects.get(pk=3).is_before_start())

    def test_is_after_end(self):
        self.assertFalse(Questionnaire.objects.get(pk=3).is_after_end())
        self.assertTrue(Questionnaire.objects.get(pk=4).is_after_end())

    def test_is_open(self):
        self.assertFalse(Questionnaire.objects.get(pk=2).is_open())
        self.assertTrue(Questionnaire.objects.get(pk=3).is_open())
        self.assertFalse(Questionnaire.objects.get(pk=4).is_open())

    def test_validate_as_false(self):
        post_data = {
                'question_1': "1",
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_2_selectiveanswer_5': "1",
                'question_3': "some content",
                }
        errors = Questionnaire.objects.get(pk=1).validate(post_data)
        self.assertListEqual(list(errors.keys()), ['question_2'])

    def test_validate_as_true(self):
        post_data = {
                'question_1': "1",
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_3': "some content",
                }
        errors = Questionnaire.objects.get(pk=1).validate(post_data)
        self.assertListEqual(list(errors.keys()), [])

    def test_accept_answered_all(self):
        post_data = {
                'question_1': "1",
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_3': "some content",
                }
        Questionnaire.objects.get(pk=1).accept(post_data)
        self.assertEqual(SelectiveAnswer.objects.get(pk=1).num, 1)
        self.assertEqual(SelectiveAnswer.objects.get(pk=3).num, 1)
        self.assertEqual(SelectiveAnswer.objects.get(pk=4).num, 1)
        self.assertEqual(TextAnswer.objects.count(), 1)

    def test_accept_blank_textanswer(self):
        post_data = {
                'question_1': "1",
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_3': "",
                }
        Questionnaire.objects.get(pk=1).accept(post_data)
        self.assertEqual(SelectiveAnswer.objects.get(pk=1).num, 1)
        self.assertEqual(SelectiveAnswer.objects.get(pk=3).num, 1)
        self.assertEqual(SelectiveAnswer.objects.get(pk=4).num, 1)
        self.assertEqual(TextAnswer.objects.count(), 0)

    def test_dump_as_csv(self):
        post_data = {
                'question_1': "1",
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_3': "some content",
                }
        Questionnaire.objects.get(pk=1).accept(post_data)

        questionnaire = Questionnaire.objects.get(pk=1)
        csv = questionnaire.dump_as_csv('utf8')
        rows = []
        for line in csv.decode('utf8').splitlines():
            rows.append(line.rstrip().split(','))
        self.assertListEqual(rows[0], ['"1st question"'])
        self.assertListEqual(rows[1], ['', '"Answer"', '"Percentage"', '"Number"'])
        self.assertListEqual(rows[2], ['', '"1st answer"', '"100.0"', '1'])
        self.assertListEqual(rows[3], ['', '"2nd answer"', '"0.0"', '0'])
        self.assertListEqual(rows[4], ['"2nd question"'])
        self.assertListEqual(rows[5], ['', '"Answer"', '"Percentage"', '"Number"'])
        self.assertListEqual(rows[6], ['', '"1st answer"', '"50.0"', '1'])
        self.assertListEqual(rows[7], ['', '"2nd answer"', '"50.0"', '1'])
        self.assertListEqual(rows[8], ['', '"3rd answer"', '"0.0"', '0'])
        self.assertListEqual(rows[9], ['"3rd question"'])
        self.assertListEqual(rows[10], ['', '"Answer"'])
        self.assertListEqual(rows[11], ['', '"some content"'])


class QuestionTests(TestCase):
    fixtures = ['user.json', 'urlkey.json', 'questionnaire.json', 'question.json', 'selectiveanswer.json', 'textanswer.json']

    def test_validate_form_type(self):
        with self.assertRaises(ValidationError):
            questionnaire = Questionnaire.objects.get(pk=1)
            Question(
                    questionnaire=questionnaire,
                    content='some content',
                    form_type=0,
                    min_num_answers=1,
                    max_num_answers=1
                    ).full_clean()

    def test_adjust_max_num_answers(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        Question(
                questionnaire=questionnaire,
                content='some content',
                form_type=Question.FORM_TYPE_SELECTION,
                min_num_answers=3,
                max_num_answers=1
                ).save()
        self.assertEqual(Question.objects.last().min_num_answers, 3)
        self.assertEqual(Question.objects.last().max_num_answers, 3)

    def test_save_on_form_type_selection(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        Question(
                questionnaire=questionnaire,
                content='some content',
                form_type=Question.FORM_TYPE_SELECTION,
                min_num_answers=1,
                max_num_answers=3
                ).save()
        self.assertEqual(Question.objects.last().min_num_answers, 1)
        self.assertEqual(Question.objects.last().max_num_answers, 3)

    def test_save_on_form_type_text(self):
        questionnaire = Questionnaire.objects.get(pk=1)
        Question(
                questionnaire=questionnaire,
                content='some content',
                form_type=Question.FORM_TYPE_TEXT,
                min_num_answers=1,
                max_num_answers=1
                ).save()
        self.assertEqual(Question.objects.last().min_num_answers, None)
        self.assertEqual(Question.objects.last().max_num_answers, None)

    def test_is_radio(self):
        self.assertTrue(Question.objects.get(pk=1).is_radio())
        self.assertFalse(Question.objects.get(pk=2).is_radio())

    def test_validate_num_answers_as_false(self):
        post_data = {
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                'question_2_selectiveanswer_5': "1",
                }
        is_valid, selectiveanswer_ids = Question.objects.get(pk=2).validate_num_answers(post_data)
        self.assertFalse(is_valid)

    def test_validate_num_answers_as_true(self):
        post_data = {
                'question_2_selectiveanswer_3': "1",
                'question_2_selectiveanswer_4': "1",
                }
        is_valid, selectiveanswer_ids = Question.objects.get(pk=2).validate_num_answers(post_data)
        self.assertTrue(is_valid)
        self.assertListEqual(selectiveanswer_ids, [3, 4])

    def test_sum_selectiveanswer_num(self):
        question = Question.objects.get(pk=1)
        for selectiveanswer in question.selectiveanswer_set.all():
            selectiveanswer.num = F('num') + 1
            selectiveanswer.save()
        self.assertEqual(question.sum_selectiveanswer_num(), 2)

    def test_limit_textanswers(self):
        textanswers = Question.objects.get(pk=3).limit_textanswers(limit=1)
        self.assertEqual(len(textanswers), 1)
        self.assertEqual(textanswers[0].id, 2)
        textanswers = Question.objects.get(pk=3).limit_textanswers(order='asc')
        self.assertEqual(len(textanswers), 2)
        self.assertEqual(textanswers[0].id, 1)



class SelectiveAnswerTests(TestCase):
    fixtures = ['user.json', 'urlkey.json', 'questionnaire.json', 'question.json', 'selectiveanswer.json']

    def test_percentage(self):
        question = Question.objects.get(pk=1)
        for selectiveanswer in question.selectiveanswer_set.all():
            selectiveanswer.num = F('num') + 1
            selectiveanswer.save()
        self.assertEqual(question.selectiveanswer_set.all().first().percentage(), 50.00)


class TextAnswerTests(TestCase):
    fixtures = ['user.json', 'urlkey.json', 'questionnaire.json', 'question.json', 'textanswer.json']

    def test_paginate_without_max_id(self):
        question = Question.objects.get(pk=3)
        pager = TextAnswer.paginate(question.id, limit=1)
        self.assertEqual(len(pager['textanswers']), 1)
        self.assertEqual(pager['next_max_id'], 1)

    def test_paginate_with_max_id(self):
        question = Question.objects.get(pk=3)
        pager = TextAnswer.paginate(question.id, max_id=1, limit=1)
        self.assertEqual(len(pager['textanswers']), 1)
        self.assertEqual(pager['next_max_id'], None)


class CSVDumperTests(TestCase):

    def test_dump(self):
        matrix = [
                ['あ', 'い', 'う'],
                ['か', 'き'],
                ['"']
                ]
        expected = '"あ","い","う"\n"か","き"\n""""'.encode('utf8', 'ignore')
        self.assertEqual(CSVDumper.dump(matrix, 'utf8'), expected)
