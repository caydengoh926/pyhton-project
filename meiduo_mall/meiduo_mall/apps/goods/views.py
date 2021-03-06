# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime

from models import GoodsCategory, SKU, GoodsVisitCount
from contents.utils import get_categories
from utils import get_bread_crumb
from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderGoods, OrderInfo

# Create your views here.


class GoodsCommentView(View):

    def get(self, request, sku_id):

        try:
            order_goods_list = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')[:30]
        except Exception as e:
            return http.HttpResponseNotFound('sku id incorrect')

        comment_list = []
        for order_goods in order_goods_list:
            username = order_goods.order.user.username
            comment_list.append({
                'username' : username[0] + '***' + username[-1] if order_goods.is_anonymous else username,
                'comment' : order_goods.comment,
                'score' : order_goods.score
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg':'OK', 'comment_list':comment_list})



class DetailVisitView(View):

    def post(self, request, category_id):

        try:
            category = GoodsCategory.objects.get(id = category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('category not found')

        t = timezone.localtime()

        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)

        today_date = datetime.strptime(today_str, '%Y-%m-%d')

        try:
            counts_data = GoodsVisitCount.objects.get(date = today_date, category = category)
        except GoodsVisitCount.DoesNotExist:
            counts_data = GoodsVisitCount()

        try:
            counts_data.date = today_date
            counts_data.category = category
            counts_data.count += 1
            counts_data.save()
        except Exception as e:
            return http.HttpResponseServerError('count failed')

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})


class DetailView(View):
    """???????????????"""

    def get(self, request, sku_id):
        """?????????????????????"""
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            # return http.HttpResponseNotFound('sku not found')
            render(request, '404.html')

        categories = get_categories()

        breadcrumb = get_bread_crumb(sku.category)

        # ??????????????????????????????
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # ???????????????????????????SKU
        skus = sku.spu.sku_set.all()
        # ???????????????????????????????????????sku??????
        spec_sku_map = {}
        for s in skus:
            # ??????sku???????????????
            s_specs = s.specs.order_by('spec_id')
            # ????????????????????????-sku????????????
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # ???????????????-sku??????????????????
            spec_sku_map[tuple(key)] = s.id
        # ?????????????????????????????????
        goods_specs = sku.spu.specs.order_by('id')
        # ?????????sku??????????????????????????????????????????
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # ????????????sku????????????
            key = sku_key[:]
            # ??????????????????
            spec_options = spec.options.all()
            for option in spec_options:
                # ???????????????sku????????????????????????????????????sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        context = {
            'categories' : categories,
            'breadcrumb' : breadcrumb,
            'sku' : sku,
            'specs' : goods_specs,
        }
        return render(request, 'detail.html', context)


class HotGoodView(View):

    def get(self, request, category_id):

        skus = SKU.objects.filter(category_id= category_id, is_launched=True).order_by('-sales')[:2]

        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            }
            hot_skus.append(sku_dict)

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'hot_skus':hot_skus})


class ListView(View):

    def get(self, request, category_id, page_num):

        try:
            category = GoodsCategory.objects.get(id = category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('parameter not exist')

        sort = request.GET.get('sort', 'default')

        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'

        categories = get_categories()

        breadcrumb = get_bread_crumb(category)

        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)

        paginator = Paginator(skus, 5)

        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        contents= {
            'categories':categories,
            'breadcrumb':breadcrumb,
            'page_skus': page_skus,
            'total_page': total_page,
            'sort': sort,
            'category_id': category_id,
            'page_num': page_num
        }

        return render(request, 'list.html', contents)

