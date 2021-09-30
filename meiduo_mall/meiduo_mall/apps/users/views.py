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
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.utils import generate_verify_email_url, check_verify_email_token
from . import constants
from goods.models import SKU
from carts.utils import merge_carts_cookie_redis
logger = logging.getLogger('django')


class UserBrowseHistory(LoginRequiredJSONMixin, View):

    def post(self, request):

        json_str = request.body.decode('utf8')
        json_dict = json.loads(json_str)
        sku_id = json_dict.get('sku_id')

        try:
            SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id not found')

        redis_conn = get_redis_connection('history')
        user = request.user

        pl = redis_conn.pipeline()
        pl.lrem('history_%s' % user.id, 0, sku_id )

        pl.lpush('history_%s' % user.id, sku_id)

        pl.ltrim('history_%s' % user.id, 0, 4)

        pl.execute()

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})

    def get(self, request):

        user = request.user

        redis_conn = get_redis_connection('history')

        sku_ids = redis_conn.lrange('history_%s' % user.id, 0, -1)

        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id = sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg': 'OK', 'skus':skus})


class ChangePasswordView(LoginRequiredMixin, View):

    def get(self, request):

        return render(request, 'user_center_pass.html')

    def post(self, request):

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('parameter empty')

        try:
            request.user.check_password(old_password)
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('new password not match with second')

        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response


class UpdateTitleAddressView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):

        json_dict = json.loads(request.body.decode('utf8'))
        title = json_dict.get('title')

        if not title:
            return http.HttpResponseForbidden('parameter title missing')

        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'edit title failed'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'edit title successful'})


class DefaultAddressView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'default address failed'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'default address successful'})


class UpdateDestroyAddressView(LoginRequiredMixin, View):

    def put(self, request, address_id):
        json_str = request.body.decode('utf8')
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^01[3-9]\d{7}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'edit address failed'})

        address = Address.objects.get(id = address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'address':address_dict})

    def delete(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'delete address unsuccessful'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class AddressCreateView(LoginRequiredJSONMixin, View):

    def post(self, request):

        count = request.user.addresses.count()
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR, 'errmsg':'add address limit exceed'})

        json_str = request.body.decode('utf8')
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^01[3-9]\d{7}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'add address failed'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'add address success', 'address':address_dict})


class AddressView(View):

     def get(self, request):
    #
        # login_user = request.user
    #   addresses = Address.objects.filter(user=login_user, is_deleted=False)
    #
    #     address_list = []
    #
    #     for address in addresses:
    #         address_dict={
    #             "id": address.id,
    #             "title": address.title,
    #             "receiver": address.receiver,
    #             "province": address.province.name,
    #             "city": address.city.name,
    #             "district": address.district.name,
    #             "place": address.place,
    #             "mobile": address.mobile,
    #             "tel": address.tel,
    #             "email": address.email
    #         }
    #         address_list.append(address_dict)
    #
    #     context = {
    #         'default_address_id': login_user.default_address_id,
    #         'addresses': address_list
    #     }

        # default_address_id = login_user.default_address_id

        return render(request, 'user_center_site.html')


class GetAddress(LoginRequiredJSONMixin, View):

    def get(self, request):

        login_user = request.user

        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_list = []

        for address in addresses:
            address_dict={
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)
        default_address_id = login_user.default_address_id

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'get addresss successful', 'addresses':address_list, 'default_address_id': default_address_id})


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

        user = authenticate(request, username=username, password=password)
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

        response = merge_carts_cookie_redis(request, user, response)

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