from django.conf.urls import patterns, include, url
from web import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'satisfactory.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index),
    url(r'^signup$', views.signup),
    url(r'^login$', views.signin),
    url(r'^logout$', views.signout),
    url(r'^term_of_use$', views.term_of_use),
    url(r'^privacy_policy$', views.privacy_policy),
    url(r'^resign$', views.resign),
    url(r'^account$', views.account),
    url(r'^account/email/update$', views.account_email_update),
    url(r'^account/password/update$', views.account_password_update),
    url(r'^help$', views.help),
    url(r'^inquiry$', views.inquiry),
    url(r'^questionnaire$', views.questionnaire),
    url(r'^questionnaire/create$', views.questionnaire_create),
    url(r'^questionnaire/(\d+)$', views.questionnaire_show),
    url(r'^questionnaire/(\d+)/update$', views.questionnaire_update),
    url(r'^questionnaire/(\d+)/delete$', views.questionnaire_delete),
    url(r'^questionnaire/(\d+)/question$', views.question),
    url(r'^questionnaire/(\d+)/question/create$', views.question_create),
    url(r'^questionnaire/(\d+)/question/(\d+)/delete$', views.question_delete),
    url(r'^questionnaire/(\d+)/question/reorder$', views.question_reorder),
    url(r'^questionnaire/(\d+)/question/(\d+)/textanswer$', views.textanswer),
    url(r'^resource/(sjis|utf8)/(questionnaire)(\d+)\.csv$', views.resource_csv),
    url(r'^-/(\w+)$', views.form),
)
