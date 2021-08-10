# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views import View
from django import http
import re, json, logging
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db import DatabaseError
from django.contrib.auth import login, authenticate, logout
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

from meiduo_mall.utils.response_code import RETCODE
from users.models import User
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.utils import generate_verify_email_url, check_verify_email_token
logger = logging.getLogger('django')


class AddressView(View):

    def get(self, request):

        return render(request, 'user_center_site.html')


class VerifyEmailView(View):

    def get(self, request):

        token = request.GET.get('token')

        if not token:
            return http.HttpResponseForbidden('no token')

        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('invalid token')

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('verify email failed')

        return redirect(reverse('users:info'))

        pass


class EmailView(LoginRequiredJSONMixin, View):

    def put(self, request):
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'add email failed'})

        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})


class UserInfoView(LoginRequiredMixin, View):

    def get(self, request):

        login_url= '/login/'
        redirect_field_name = 'redirect_to'

        context = {'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


class LogoutView(View):

    def get(self, request):

        logout(request)

        response = redirect(reverse('contents:index'))

        response.delete_cookie('username')

        return response


class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if not all([username, password]):
            return http.HttpResponseForbidden('please insert username and password')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return  http.HttpResponseForbidden('请输入5-20个字符的用户名')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg':'username or password incorrect'})
        login(request, user)

        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        next = request.GET.get('next')

        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


# Create your views here.


class UsernameCountView(View):

    def get(self, request, username):

        count = User.objects.filter(username=username).count()

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'count':count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return  http.HttpResponseForbidden('请输入5-20个字符的用户名')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        if password2 != password:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        if not re.match(r'^01[3-9]\d{7}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        redis_conn = get_redis_connection('verify_code')

        sms_code_server = redis_conn.get('sms_%s' % mobile)

        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg':'sms code expired'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg':'sms code incorrect'})
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # return render(request, 'register.html', {'register_errmsg': 'registerfailed'})

        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg':'registerfailed'})

        login(request, user)
        # return http.HttpResponse('register successful')

        response = redirect(reverse('contents:index'))

        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response