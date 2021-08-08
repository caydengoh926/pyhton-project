# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import random

from django import http
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.utils.response_code import RETCODE

from celery_tasks.sms import constants
# from meiduo_mall.celery_tasks.sms.send_sms import CCP
from verifications.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.

logger = logging.getLogger('django')

class SMSCodeView(View):

    def get(self, request, mobile):

        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('param not found')

        redis_conn = get_redis_connection('verify_code')

        send_flag = redis_conn.get('send_flag_%s' % mobile)

        if send_flag:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR, 'errmsg':'sms code too frequent'})

        image_code_server = redis_conn.get('img_%s' % uuid)

        if image_code_server is None:
            return http.JsonResponse({'code':RETCODE.IMAGECODEERR, 'errmsg':'image code expires'})

        redis_conn.delete('img_%s' % uuid)

        image_code_server = image_code_server.decode()

        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'image code incorrect'})

        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # redis_conn.setex('sms_%s' % mobile, constants.IMAGE_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        pl = redis_conn.pipeline()

        pl.setex('sms_%s' % mobile, constants.IMAGE_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        pl.execute()

        # CCP().sendTemplateSMS('+6%s' % mobile, sms_code)
        send_sms_code.delay(mobile, sms_code)

        return http.JsonResponse({'code': RETCODE.OK , 'errmsg':'sending successful'})

class ImageCodeView(View):

    def get(self, request, uuid):

        text,image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_code')

        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return http.HttpResponse(image, content_type='image/jpg')
