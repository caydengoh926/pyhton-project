from django.conf.urls import url

from . import views

urlpatterns=[
    url(r'^image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view()),

    url(r'^sms_codes/(?P<mobile>01[3-9]\d{7})/$', views.SMSCodeView.as_view()),
]