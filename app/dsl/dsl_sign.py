#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : dsl_sign.py
# @Time    : 2022/5/9 2:14 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import requests
from conf.config import DSL_CONF

class DslSign:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        self.token = kwargs.get('token', None)

        self.http = requests.Session()
        self.http.headers.update({
            'content-type': 'application/json',
            'host': 'crmweixin.dslbuy.com',
            'usre-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001432) NetType/WIFI Language/zh_CN',
            'referer': 'https://servicewechat.com/wx16ed9a8bbb188228/343/page-frame.html',
        })

    def sign(self):
        """
        :return:
        """
        url = 'https://crmweixin.dslbuy.com/integralmall/userSign/add.do?mobile=&type=1&mini_token={}'.format(self.token)
        response = self.http.get(url)
        print('大参林签到结果:', response.json())

    def run(self):
        """
        :return:
        """
        self.sign()


if __name__ == '__main__':
    token_list = DSL_CONF.get('token')
    for tk in token_list:
        app = DslSign(token=tk)
        app.run()
