# -*- encoding: utf-8 -*-

'''
通知函数
'''

from djmail.template_mail import InlineCSSTemplateMail


def _email(to, params):
    o = InlineCSSTemplateMail(params['level'])
    o.send(to, params)


def _sms(to, params):
    pass


def _wechat(to, params):
    pass


FUNCS = {
    'wechat': _wechat,
    'email': _email,
    'sms': _sms
}


def alert(to, params):
    for tp in to:
        func = FUNCS[tp]
        func(to[tp], params)
