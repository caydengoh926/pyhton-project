from celery_tasks.sms.send_sms import CCP
from celery_tasks.main import celery_app


@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    try:
        send_ret = CCP().sendTemplateSMS('+6%s' % mobile, sms_code)
        return send_ret
    except Exception as e:
        raise self.retry(exc=e, max_retries=3)