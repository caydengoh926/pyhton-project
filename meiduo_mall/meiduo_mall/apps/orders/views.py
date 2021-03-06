# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage

from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJSONMixin
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


class OrderCommentView(LoginRequiredMixin, View):

    def get(self, request):

        order_id = request.GET.get('order_id')
        user = request.user

        try:
            OrderInfo.objects.get(order_id= order_id, user = user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('orderid doesnt exist')

        try:
            uncomment_goods = OrderGoods.objects.filter(order_id= order_id, is_commented= False)
        except Exception as e:
            return http.HttpResponseServerError('orders incorrect')

        uncomment_goods_list = []
        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id' : goods.order.order_id,
                'sku_id' : goods.sku.id,
                'name' : goods.sku.name,
                'price' : str(goods.price),
                'score' : goods.score,
                'comments' : goods.comment,
                'default_image' : goods.sku.default_image.url,
                'is_anonymous' : str(goods.is_anonymous)
            })

        context = {
            'uncomment_goods_list': json.dumps(uncomment_goods_list)
        }

        return render(request, 'goods_judge.html', context)

    def post(self, request):

        json_str = request.body.decode('utf8')
        json_dict = json.loads(json_str)
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        comment = json_dict.get('comment')
        score = json_dict.get('score')
        is_anonymous = json_dict.get('is_anonymous')
        user = request.user

        if not all([order_id, sku_id, comment, score]):
            return http.HttpResponseForbidden('??????????????????')

        try:
            OrderInfo.objects.filter(order_id=order_id, user = user, status= OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('orderid parameter incorrect')

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku incorrect')

        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('??????is_anonymous??????')

        OrderGoods.objects.filter(order_id=order_id, sku_id= sku_id, is_commented= False).update(
            comment = comment,
            score = score,
            is_anonymous = is_anonymous,
            is_commented = True
        )
        comments = sku.comments + 1
        SKU.objects.filter(id=sku_id).update(comments = comments)
        sku.spu.comments += 1
        sku.spu.save()
        # sku.save()

        if OrderGoods.objects.filter(order_id=order_id, sku_id= sku_id, is_commented= False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(
                status = OrderInfo.ORDER_STATUS_ENUM['FINISHED']
            )

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg': 'Comment successful'})


class UserOrderInfoView(LoginRequiredMixin, View):

    def get(self, request, page_num):

        user = request.user

        orders = user.orderinfo_set.all().order_by('-create_time')

        for order in orders:
            # ??????????????????
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]

            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]

            order.sku_list = []

            order_goods = order.skus.all()

            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.count * sku.price
                order.sku_list.append(sku)

        page_num = int(page_num)
        try:
            paginator = Paginator(orders, 3)

            page_orders = paginator.page(page_num)

            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('???????????????')

        context = {
            'page_orders':page_orders,
            'total_page' : total_page,
            'page_num' : page_num

        }

        return render(request, 'user_center_order.html', context)


class OrderSuccessView(LoginRequiredMixin, View):

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount' : payment_amount,
            'pay_method': pay_method
        }

        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequiredJSONMixin, View):

    def post(self, request):

        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # ????????????
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('??????????????????')
        # ??????address_id????????????
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('??????address_id??????')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
            return http.HttpResponseForbidden('??????pay_method??????')

        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                user = request.user
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S')+('%09d' % user.id)

                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal(0.00),
                    freight = Decimal(10.00),
                    pay_method = pay_method,
                    status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM["ALIPAY"] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                redis_conn = get_redis_connection('carts')

                redis_cart = redis_conn.hgetall('carts_%s' % user.id)

                redis_selected = redis_conn.smembers('selected_%s' % user.id)

                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

                sku_ids = new_cart_dict.keys()

                for sku_id in sku_ids:

                    while True:
                        sku = SKU.objects.get(id = sku_id)

                        sku_count = new_cart_dict[sku.id]

                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        if sku_count > origin_stock:
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code':RETCODE.STOCKERR, 'errmsg':'????????????'})

                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        new_stock = origin_stock + sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id = sku_id, stock= origin_stock).update(stock= new_stock, sales= new_sales)
                        if result == 0:
                            continue

                        sku.spu.sales += sku_count
                        sku.spu.save()

                        OrderGoods.objects.create(
                            order = order,
                            sku = sku,
                            count = sku_count,
                            price = sku.price,
                        )
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price

                        break

                order.total_amount += order.freight
                order.save()

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '????????????'})

            transaction.savepoint_commit(save_id)

            pl = redis_conn.pipeline()
            pl.hdel('carts_%s' % user.id, *redis_selected)
            pl.srem('selected_%s' % user.id, *redis_selected)
            pl.execute()

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'order_id':order_id})


class OrderSettlementView(LoginRequiredMixin, View):

    def get(self, request):

        user = request.user
        try:
            addresses = Address.objects.filter(user = user, is_deleted = False)
        except Exception as e:
            addresses = None

        redis_conn = get_redis_connection('carts')

        redis_cart = redis_conn.hgetall('carts_%s' % user.id)

        redis_selected = redis_conn.smembers('selected_%s' % user.id)

        new_cart_dict ={}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in = sku_ids)

        total_count = 0
        total_payment = Decimal(0.00)

        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            total_count += sku.count
            total_payment += sku.amount

        freight = Decimal(10.00)

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_payment,
            'freight': freight,
            'payment_amount': total_payment + freight
        }

        return render(request, 'place_order.html', context)