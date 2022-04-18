#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : qds_sign.py
# @Time    : 2022/5/9 11:42 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 0 9 * * *
# @Desc    : 丘大叔签到
import requests

from conf.config import QDS_CONF


class Qds:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        token = kwargs.get('token', None)
        self.http = requests.Session()
        self.http.headers.update({
            'Qm-User-Token': token,
            'store-id': '202338',
            'content-type': 'application/json',
            'host': 'webapi.qmai.cn',
            'Qm-From': 'wechat',
            'Qm-From-Type': 'catering',
            'scene': '1001',
            'qz-gtd': ''
        })

    def sign(self):
        """
        :return:
        """
        url = 'https://webapi.qmai.cn/web/catering/integral/sign/signIn'
        params = {
            "activityId": "100820000000000642",
            "mobilePhone": "19128151871",
            "userName": "林同学",
            "appid": "wx01d44c5a2232d2d0"
        }
        response = self.http.post(url, json=params)
        res = response.json()
        print('签到结果:', res)

    def query(self):
        """
        查询积分
        :return:
        """
        url = 'https://webapi.qmai.cn/web/catering/crm/points-info'
        params = {
            "appid": "wx01d44c5a2232d2d0"
        }
        response = self.http.post(url, json=params)
        data = response.json()
        print('当前积分:', data.get('data'))

    def run(self):
        """
        :return:
        """
        self.sign()
        self.query()


if __name__ == '__main__':
    token_list = QDS_CONF.get('token')
    print('开始执行《丘大叔柠檬茶签到》....')
    for tk in token_list:
        app = Qds(token=tk)
        app.run()
    print('《丘大叔柠檬茶签到》执行完成....')
