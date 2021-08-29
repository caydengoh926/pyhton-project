# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json, base64, pickle
from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class CartsSimpleView(View):

    def get(self, request):

        user = request.user

        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            cart_selected = redis_conn.smembers('selected_%s' % user.id)
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                        'count' :int(count),
                        'selected':sku_id in cart_selected
                        }
        else:

            carts_str = request.COOKIES.get('carts')
            if carts_str:
                cart_str_byte = carts_str.encode()

                cart_dict_byte = base64.b64decode(cart_str_byte)

                cart_dict = pickle.loads(cart_dict_byte)
            else:
                cart_dict = {}

        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in= sku_ids)
        for sku in skus:
            cart_skus.append({
                'id' : sku.id,
                'name' : sku.name,
                'count' : cart_dict.get(sku.id).get('count'),
                'default_image_url' : sku.default_image.url
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})


class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)

            redis_sku_ids = redis_cart.keys()

            if selected:
                redis_conn.sadd('selected_%s' % user.id, *redis_sku_ids)
            else:
                redis_conn.srem('selected_%s' % user.id, *redis_sku_ids)

            return http.JsonResponse({'code':RETCODE.OK, 'errmsg': 'OK'})

        else:
            # 用户已登录，操作cookie购物车
            carts_str = request.COOKIES.get('carts')

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            if carts_str:
                cart_str_byte = carts_str.encode()

                cart_dict_byte = base64.b64decode(cart_str_byte)

                cart_dict = pickle.loads(cart_dict_byte)

                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected

                cart_dict_bytes = pickle.dumps(cart_dict)

                cart_str_bytes = base64.b64encode(cart_dict_bytes)

                cookie_cart_str = cart_str_bytes.decode()

                response.set_cookie('carts', cookie_cart_str)

            return response


class CartsView(View):

    def post(self, request):

        json_str = request.body.decode('utf8')
        json_dict = json.loads(json_str)
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if not all([sku_id, count]):
            return http.HttpResponseForbidden('parameter missing')
        try:
            SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('incorrect sku_id')
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('parameter incorrect')
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('parameter incorrect')

        user = request.user
        if user.is_authenticated:

            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()

            pl.hincrby('carts_%s' % user.id, sku_id, count)

            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})

            pass
        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                cart_str_byte = carts_str.encode()

                cart_dict_byte = base64.b64decode(cart_str_byte)

                cart_dict = pickle.loads(cart_dict_byte)
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            cart_dict_bytes = pickle.dumps(cart_dict)

            cart_str_bytes = base64.b64encode(cart_dict_bytes)

            cookie_cart_str = cart_str_bytes.decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg':'OK'})

            response.set_cookie('carts', cookie_cart_str)

            return response

    def get(self, request):
        """展示购物车"""
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询redis购物车
            redis_conn = get_redis_connection('carts')

            redis_cart = redis_conn.hgetall('carts_%s' % user.id)

            redis_selected = redis_conn.smembers('selected_%s' % user.id)

            cart_dict = {}
            for sku_id , count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }

        else:
            # 用户未登录，查询cookies购物车
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                cart_str_byte = carts_str.encode()

                cart_dict_byte = base64.b64decode(cart_str_byte)

                cart_dict = pickle.loads(cart_dict_byte)
            else:
                cart_dict = {}

        sku_ids = cart_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)

        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus': json.dumps(cart_skus),
        }

        return render(request, 'cart.html', context)

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，修改redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()

            pl.hset('carts_%s' % user.id, sku_id, count)

            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            # 用户未登录，修改cookie购物车
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                cart_str_byte = carts_str.encode()

                cart_dict_byte = base64.b64decode(cart_str_byte)

                cart_dict = pickle.loads(cart_dict_byte)
            else:
                cart_dict = {}

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }

            cart_dict_bytes = pickle.dumps(cart_dict)

            cart_str_bytes = base64.b64encode(cart_dict_bytes)

            cookie_cart_str = cart_str_bytes.decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})

            response.set_cookie('carts', cookie_cart_str)

            return response

    def delete(self, request):
        """删除购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户未登录，删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_%s' % user.id , sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})

        else:
            # 用户未登录，删除cookie购物车
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                cart_str_byte = carts_str.encode()

                cart_dict_byte = base64.b64decode(cart_str_byte)

                cart_dict = pickle.loads(cart_dict_byte)
            else:
                cart_dict = {}

            response = http.JsonResponse({'code':RETCODE.OK, 'errmsg': 'OK'})

            if sku_id in cart_dict:
                del cart_dict[sku_id]

                cart_dict_bytes = pickle.dumps(cart_dict)

                cart_str_bytes = base64.b64encode(cart_dict_bytes)

                cookie_cart_str = cart_str_bytes.decode()

                response.set_cookie('carts', cookie_cart_str)

            return response