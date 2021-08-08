from meiduo_mall.celery_tasks.sms.send_sms import CCP

if __name__ == '__main__':
    CCP().sendTemplateSMS("+60163210514", 123456)