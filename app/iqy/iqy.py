#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : iqy.py
# @Time    : 2022/5/9 2:31 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import requests
from conf.config import IQY_CONF


class IqySign:

    def __init__(self, **kwargs):
        self.url = kwargs.get('url', '')
        self.http = requests.Session()
        self.http.headers.update({
            'user-agent': 'QIYIVideo/13.4.5 (iOS;com.qiyi.iphone;iOS15.4.1;iPhone14,2) Corejar',
            'content-type': 'application/json',
            'X-B3-TraceId': 'dfc4c813a95f8058ba7f7ca780010000',
            'X-B3-SpanId': 'ba7f7ca780010000',
            'sign': 'dfe998899b09535d60d4cb299e2f73bc',
        })

    def sign(self):
        """
        :return:
        """
        params = {
            "natural_month_sign": {
                "verticalCode": "iQIYI",
                "taskCode": "iQIYI_mofhr",
                "authCookie": "3egMm2Cbphm3EGlPJOKJX7eF8eurUTRQum2BjKd2Y0rvVaJCRa4hV9fDhxeQfq0Zp5yARea",
                "agentVersion": "13.4.5",
                "agentType": "20",
                "qyid": "a73c75daec2b8e0b387f7c4c7df2cf2a1111"
            }
        }
        response = self.http.post(self.url, json=params)

        print('爱奇艺签到结果:', response.json().get('data'))

    def run(self):
        self.sign()


if __name__ == '__main__':
    url_list = IQY_CONF.get('urls')
    for item in url_list:
        app = IqySign(url=item)
        app.run()
