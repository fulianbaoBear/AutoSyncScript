#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : xc_sign.py
# @Time    : 2022/5/9 10:39 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 1 9 * * *
# @Desc    : 喜茶签到
import requests
from conf.config import XC_CONF


class NxSign:

    def __init__(self, **kwargs):
        token = kwargs.get('token', None)
        if not token:
            raise ValueError('Missing token...')

        self.http = requests.Session()
        self.http.headers.update({
            'Authorization': token,
            'x-client': 'weapp',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001432) NetType/WIFI Language/zh_CN miniProgram/wxab7430e6e8b9a4ab',
            'referer': 'https://servicewechat.com/wx696a42df4f2456d3/708/page-frame.html'
      })

    def sign(self):
        """
        :return:
        """
        url = 'https://vip.heytea.com/api/service-member/vip/task/award/114'
        data = {}
        response = self.http.post(url, json=data)
        res = response.json()
        print('喜茶签到结果:', res.get('message', '未知'))

    def query(self):
        """
        :return:
        """
        url = 'https://vip.heytea.com/api/service-member/vip/coupon-library/point-coupon'
        data = {}
        response = self.http.get(url, json=data)
        res = response.json()
        score = res.get('data', dict()).get('usableScore', -1)
        print('当前喜茶积分:', score)

    def run(self):
        """
        :return:
        """
        self.sign()
        self.query()


if __name__ == '__main__':
    token_list = XC_CONF.get('token')
    for tk in token_list:
        app = NxSign(token=tk)
        app.run()
