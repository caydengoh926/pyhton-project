# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views import View
from django import http
from django.core.cache import cache
import logging

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')

# Create your views here.


class AreasView(View):

    def get(self,request):

        area_id = request.GET.get('area_id')

        if not area_id:
            province_list = cache.get('province_list')

            if not province_list:

                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)

                    province_list=[]
                    for province_model in province_model_list:
                        province_dict = {
                            "id":province_model.id,
                            "name":province_model.name
                        }
                        province_list.append(province_dict)

                    cache.set('province_list', province_list, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'query databases error'})

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        else:
            sub_data = cache.get('sub_area_' + area_id)

            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()

                    subs=[]
                    for sub_model in sub_model_list:
                        sub_dict={
                            'id': sub_model.id,
                            'name': sub_model.name,
                        }
                        subs.append(sub_dict)

                    sub_data = {
                            'id': parent_model.id,
                            'name': parent_model.name,
                            'subs':subs
                    }

                    cache.set('sub_area_' + area_id, sub_data, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'query databases error'})

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})

