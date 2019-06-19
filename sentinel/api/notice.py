# -*- encoding: utf-8 -*-

'''
通知函数
'''

from djmail.template_mail import InlineCSSTemplateMail


def email(to, params):
    o = InlineCSSTemplateMail(params['level'])
    o.send(to, params)


def sms(to, params):
    pass


def wechat(to, params):
    pass
