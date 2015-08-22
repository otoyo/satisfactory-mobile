import csv
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.conf import settings
from web.models import *
from web.forms import *
from web.decorators import post_required

def with_default_param(param):
    return dict({'debug': settings.DEBUG}, **param)

def index(request):
    return render(request, 'web/index.html', with_default_param({}))

def signup(request):
    if request.method == 'POST':
        errors = {}
        post_data = request.POST
        form = SignupForm(request.POST)
        if not form.is_valid():
            errors = form.errors
        data = form.cleaned_data
        # TODO: Refactor uniqueness check
        if User.objects.filter(username=data['username']).exists():
            errors['username_uniqueness'] = []
        if User.objects.filter(email=data['email']).exists():
            errors['email_uniqueness'] = []
        if errors:
            return render(request, 'web/signup.html', with_default_param({
                'errors': errors,
                'post_data': post_data,
                }))
        user = User.objects.create_user(
                data['username'], data['email'], data['password'])
        return render(request, 'web/welcome.html', with_default_param({}))
    return render(request, 'web/signup.html', with_default_param({}))

def signin(request):
    if request.method == 'POST':
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/questionnaire')

    msg = {}
    if 'msg' in request.session.keys():
        msg = request.session.pop('msg')

    return render(request, 'web/login.html', with_default_param({
        'is_invalid': request.method == 'POST',
        'msg': msg
        }))

def signout(request):
    logout(request)
    return redirect('/login')

def term_of_use(request):
    return render(request, 'web/term_of_use.html', with_default_param({}))

def privacy_policy(request):
    return render(request, 'web/privacy_policy.html', with_default_param({}))

@post_required
@login_required
def resign(request):
    Questionnaire.objects.filter(user_id=request.user.id).update(is_public=False)
    request.user.is_active = False
    request.user.save()
    logout(request)
    return render(request, 'web/resign.html', with_default_param({}))

@login_required
def account(request):
    errors = {}
    if 'errors' in request.session.keys():
        errors = request.session.pop('errors')

    msg = {}
    if 'msg' in request.session.keys():
        msg = request.session.pop('msg')

    return render(request, 'web/account/index.html', with_default_param({
        'user': request.user,
        'errors': errors,
        'msg': msg
        }))

@post_required
@login_required
def account_email_update(request):
    form = EmailForm(request.POST)
    if not form.is_valid():
        request.session['errors'] = form.errors
        request.session['post_data'] = request.POST
        return redirect('/account#email-edit')

    request.user.email = form.cleaned_data['email']
    request.user.save()

    request.session['msg'] = {
            'action': 'update', 'result': 'success', 'target': 'email'}
    return redirect('/account')

@post_required
@login_required
def account_password_update(request):
    errors = {}
    form = PasswordForm(request.POST)
    if not form.is_valid():
        errors = form.errors
    data = form.cleaned_data
    if not request.user.check_password(data['current_password']):
        errors['current_password'] = []
    if errors:
        request.session['errors'] = errors
        return redirect('/account#password-edit')

    request.user.set_password(data['password'])
    request.user.save()

    user = authenticate(username=request.user.username, password=data['password'])
    login(request, user)

    request.session['msg'] = {
            'action': 'update', 'result': 'success', 'target': 'password'}
    return redirect('/account')

@login_required
def help(request):
    helps = Help.objects.all()
    return render(request, 'web/help.html', with_default_param({'helps': helps}))

def inquiry(request):
    return render(request, 'web/inquiry.html', with_default_param({}))

@login_required
def questionnaire(request):
    errors = {}
    if 'errors' in request.session.keys():
        errors = request.session.pop('errors')

    post_data = {}
    if 'post_data' in request.session.keys():
        post_data = request.session.pop('post_data')

    msg = {}
    if 'msg' in request.session.keys():
        msg = request.session.pop('msg')

    questionnaire_list = Questionnaire.listup_by_user_id(request.user.id)
    questionnaire_count = Questionnaire.objects.filter(user_id=request.user.id).count()
    return render(request, 'web/questionnaire/index.html', with_default_param({
        'highlighted_questionnaire_ids': request.session.get('highlighted_questionnaire_ids', []),
        'questionnaire_list': questionnaire_list,
        'questionnaire_count': questionnaire_count,
        'questionnaire_limit': settings.DEFAULT_QUESTIONNAIRE_LIMIT,
        'errors': errors,
        'post_data': post_data,
        'msg': msg
        }))

@post_required
@login_required
def questionnaire_create(request):
    questionnaire_count = Questionnaire.objects.filter(user_id=request.user.id).count()
    if not questionnaire_count < settings.DEFAULT_QUESTIONNAIRE_LIMIT:
        raise Http404

    form = QuestionnaireForm(request.POST)
    if not form.is_valid():
        request.session['errors'] = form.errors
        request.session['post_data'] = request.POST
        return redirect('/questionnaire#new')
    questionnaire = form.save(commit=False)
    questionnaire.user = request.user
    questionnaire.set_urlkey()
    questionnaire.save()

    if not 'highlighted_questionnaire_ids' in request.session.keys():
        request.session['highlighted_questionnaire_ids'] = []
    request.session['highlighted_questionnaire_ids'].append(questionnaire.id)

    request.session['msg'] = {
            'action': 'create', 'result': 'success', 'target': 'questionnaire'}

    return redirect('/questionnaire')

@login_required
def questionnaire_show(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    errors = {}
    if 'errors' in request.session.keys():
        errors = request.session.pop('errors')

    post_data = {}
    if 'post_data' in request.session.keys():
        post_data = request.session.pop('post_data')

    highlighted_questionnaire_ids = request.session.get('highlighted_questionnaire_ids', [])
    if questionnaire.id in highlighted_questionnaire_ids:
        highlighted_questionnaire_ids.remove(questionnaire.id)
        request.session['highlighted_questionnaire_ids'] = highlighted_questionnaire_ids

    return render(request, 'web/questionnaire/show.html', with_default_param({
        'questionnaire': questionnaire,
        'errors': errors,
        'post_data': post_data
        }))

@post_required
@login_required
def questionnaire_update(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    form = QuestionnaireForm(request.POST, instance=questionnaire)
    if not form.is_valid():
        request.session['errors'] = form.errors
        request.session['post_data'] = request.POST
        return redirect('/questionnaire/{0}#edit'.format(questionnaire.id))
    form.save()

    return redirect('/questionnaire/{0}'.format(questionnaire.id))

@post_required
@login_required
def questionnaire_delete(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    questionnaire.delete()
    request.session['msg'] = {
            'action': 'delete', 'result': 'success', 'target': 'questionnaire'}
    return redirect('/questionnaire')

@login_required
def question(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    questions = Question.objects.filter(
            questionnaire_id=questionnaire_id
            ).order_by('_order')

    errors = {}
    if 'errors' in request.session.keys():
        errors = request.session.pop('errors')

    post_data = {}
    if 'post_data' in request.session.keys():
        post_data = request.session.pop('post_data')

    msg = {}
    if 'msg' in request.session.keys():
        msg = request.session.pop('msg')

    return render(request, 'web/question/index.html', with_default_param({
        'questionnaire': questionnaire,
        'questions': questions,
        'question_limit': settings.DEFAULT_QUESTION_LIMIT,
        'errors': errors,
        'post_data': post_data,
        'msg': msg
        }))

@post_required
@login_required
def question_create(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    question_count = Question.objects.filter(questionnaire_id=questionnaire.id).count()
    if not question_count < settings.DEFAULT_QUESTION_LIMIT:
        raise Http404

    form = None
    if int(request.POST['form_type']) == Question.FORM_TYPE_SELECTION:
        form = QuestionFormForSelection(request.POST)
    else:
        form = QuestionFormForText(request.POST)
    if not form.is_valid():
        request.session['errors'] = form.errors
        request.session['post_data'] = request.POST
        return redirect('/questionnaire/{0}/question#new'.format(questionnaire.id))
    cleaned_data = form.cleaned_data

    selectiveanswers = []
    max_num_answers = None
    min_num_answers = None
    if cleaned_data['form_type'] == Question.FORM_TYPE_SELECTION:
        selectiveanswers = cleaned_data['selectiveanswer'].rstrip().splitlines()
        max_num_answers = min(len(selectiveanswers), cleaned_data['max_num_answers'])
        min_num_answers = min(len(selectiveanswers), cleaned_data['min_num_answers'])

    question = Question(
            questionnaire=questionnaire,
            content=cleaned_data['content'],
            form_type=cleaned_data['form_type'],
            max_num_answers=max_num_answers,
            min_num_answers=min_num_answers,
            )
    question.save()

    if cleaned_data['form_type'] == Question.FORM_TYPE_SELECTION:
        for content in selectiveanswers:
            question.selectiveanswer_set.create(content=content)

    request.session['msg'] = {
            'action': 'create', 'result': 'success', 'target': 'question'}

    return redirect('/questionnaire/{0}/question'.format(questionnaire.id))

@post_required
@login_required
def question_delete(request, questionnaire_id, question_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    question = Question.objects.get(pk=question_id)
    if question.questionnaire_id != questionnaire.id:
        raise Http404

    question.delete()
    request.session['msg'] = {
            'action': 'delete', 'result': 'success', 'target': 'question'}
    return redirect('/questionnaire/{0}/question'.format(questionnaire.id))

@post_required
@login_required
def question_reorder(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    question_ids = request.POST['question_ids'].rstrip().split(',')
    for question_id in question_ids:
        question = Question.objects.get(pk=question_id)
        if question.questionnaire_id != questionnaire.id:
            raise Http404

    questionnaire.set_question_order(question_ids)

    request.session['msg'] = {
            'action': 'update', 'result': 'success', 'target': 'question'}
    return redirect('/questionnaire/{0}/question'.format(questionnaire.id))

@login_required
def textanswer(request, questionnaire_id, question_id):
    questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
    if questionnaire.user.id != request.user.id:
        raise Http404

    question = Question.objects.get(pk=question_id)
    if question.questionnaire_id != questionnaire.id or question.is_selection_form_type():
        raise Http404

    max_id = None
    if (request.GET.get('i', None) and request.GET['i'].isdigit()):
        max_id = int(request.GET['i'])
    pager = TextAnswer.paginate(question.id, max_id=max_id)

    return render(request, 'web/textanswer/index.html', with_default_param({
        'questionnaire': questionnaire,
        'question': question,
        'pager': pager,
        }))

@login_required
def resource_csv(request, encoding, resource, id):
    questionnaire = Questionnaire.objects.filter(id=id).first()
    if not questionnaire:
        raise Http404

    response = HttpResponse(content_type='application/x-csv')
    response['Content-Disposition'] = 'attachment; filename="questionnaire.csv"'
    response.write(questionnaire.dump_as_csv(encoding))
    return response

def form(request, urlkey_val):
    urlkey = UrlKey.objects.filter(val=urlkey_val).first()
    if not urlkey:
        raise Http404

    questionnaire = Questionnaire.objects.filter(urlkey_id=urlkey.id).first()
    if not questionnaire or not questionnaire.is_open():
        raise Http404

    post_data = {}
    errors = {}
    if request.method == 'POST':
        post_data = request.POST
        errors = questionnaire.validate(post_data)
        if not errors:
            questionnaire.accept(post_data)
            return render(request, 'web/thankyou.html', with_default_param({
                'questionnaire': questionnaire}))
    return render(request, 'web/form.html', with_default_param({
        'post_data': post_data,
        'errors': errors,
        'questionnaire': questionnaire
        }))
