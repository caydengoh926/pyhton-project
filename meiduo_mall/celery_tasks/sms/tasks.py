from celery_tasks.sms.send_sms import CCP
from celery_tasks.main import celery_app

@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    send_ret = CCP().sendTemplateSMS('+6%s' % mobile, sms_code)
    return send_ret