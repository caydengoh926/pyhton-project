# -*- coding: utf-8 -*-
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


# Your Account SID from twilio.com/console
account_sid = "AC3750eaa7ad60ecdf261ae278357fa721"
# Your Auth Token from twilio.com/console
auth_token  = "119536fdc01007a64b13e3cfbb354afa"

# to= "+60163210514"
# vcode=123456

# def sendTemplateSMS(to, vcode):
#     client = Client(account_sid, auth_token)
#
#     message = client.messages.create(
#         to=to,
#         from_="+17198883045",
#         body="Your Meiduo_mall verification code is:%d" % vcode)
#
#     print(message.sid)

class CCP(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(CCP, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = Client(account_sid, auth_token)

        return cls._instance

    def sendTemplateSMS(self, to, vcode):
        try:
            message = self.client.messages.create(
                to=to,
                from_="+17198883045",
                body="Your Meiduo_mall verification code is:%s" % vcode
                # status_callback='https://ensa7vo5l0ag1gq.m.pipedream.net',
            )
        except TwilioRestException as e:
            print(e)

        messages = self.client.messages.list(limit=5)
        for record in messages:
            print(record.status)

        print(message.sid)
        # self.status = message.Status.SENT
        print(message)

if __name__ == '__main__':
    CCP().sendTemplateSMS("+60163210514", 123456)
    # message_status = CCP()
    # info = message_status.status
    # print(info)

