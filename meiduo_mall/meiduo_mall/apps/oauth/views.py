# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views import View
from django import http
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
import logging, re
from django_redis import get_redis_connection

from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OauthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User
from carts.utils import merge_carts_cookie_redis

# Create your views here.
logger = logging.getLogger('django')


class QQAuthUserView(View):

    def get(self, request):

        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('getcodefailed')

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        try:
            oauth_user = OauthQQUser.objects.get(openid=openid)

        except OauthQQUser.DoesNotExist:
            access_token_openid = generate_access_token(openid)
            context={'access_token_openid':access_token_openid}
            return render(request, 'oauth_callback.html', context)

        else:
            login(request, oauth_user.user)

            next = request.GET.get('next')
            response = redirect(next)

            response.set_cookie('username', oauth_user.user.username, max_age=3600 * 24 * 15)

            response = merge_carts_cookie_redis(request, oauth_user.user, response)

            return response

    def post(self,request):
        """美多商城用户绑定到openid"""
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^01[3-9]\d{7}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        openid = check_access_token(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'openid invalid'})
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist :
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg':'username or password incorrect'})
        try:
            oauth_qq_user = OauthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg':'Create user failed'})

        login(request, oauth_qq_user.user)

        next = request.GET.get('next')
        response = redirect(next)

        response.set_cookie('username', oauth_qq_user.user.username, max_age=3600 * 24 * 15)

        response = merge_carts_cookie_redis(request, user, response)

        return response



class QQAuthURLView(View):

    def get(self, request):

        next = request.GET.get('next')

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'login_url':login_url})

