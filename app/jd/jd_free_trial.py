#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_free_trial.py
# @Time    : 2022/4/21 3:24 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 40 7 * * *
# @Desc    :
import json
import time
from urllib.parse import urlencode

import requests

from app.jd import JdApp, run_jd


class JdFreeTrial(JdApp):

    def __init__(self, **kwargs):
        super(JdFreeTrial, self).__init__(**kwargs)

        self.free_trial_conf = self.conf.get('jd_free_trial', dict())
        self.keywords = self.free_trial_conf.get('keywords', '孕妇@老人@中年@幼儿园@教程@英语@辅导@培训@孩子@小学@成人用品@套套@情趣@自慰@阳具@飞机杯@男士用品@女士用品@内衣@高潮@避孕@乳腺@肛塞@肛门@宝宝@玩具@芭比@娃娃@男用@老人@女用@神油@足力健@老人@宠物@饲料@磨脚@跳蛋@阴道@阴部@龟头')
        self.max_count = self.free_trial_conf.get('max_count', 10)
        self.mini_price = self.free_trial_conf.get('mini_price', 50)
        self.categories = self.free_trial_conf.get('categories', '个人护理,服饰鞋包,闪电试,手机数码,钟表奢品,食品饮料,家用电器,电脑办公,美妆护肤').split(',')

        self.success_num = 0
        self.fail_num = 0

        self.http = None

        self.headers = {
            'referer': 'https://prodev.m.jd.com/mall/active/G7sQ92vWSBsTHzk4e953qUGWQJ4/index.html',
            'content-type': 'application/json',
            'user-agent': 'jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 '
                          'Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                          'Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36',
            'origin': 'https://prodev.m.jd.com',
            'set-fetch-site': 'same-site',
            'x-requested-with': 'com.jingdong.app.mall'
        }

        self.tab_map = {
            '服饰鞋包': '8',
            '闪电试': '2',
            '手机数码': '4',
            '钟表奢品': '12',
            '个人护理': '13',
            '食品饮料': '15',
            '家用电器': '3',
            '电脑办公': '5',
            '美妆护肤': '7'
        }

    @property
    def app_name(self):
        return "免费试用"

    def request(self, function_id, body=None):
        """
        :param body:
        :param function_id:
        :return:
        """
        if not self.http:
            self.http = requests.Session()
            self.http.cookies.update(self.cookies)
            self.http.headers.update(self.headers)

        if not body:
            body = {}

        body['geo'] = {"lng": 113.390063, "lat": 23.013134}
        body.update({
            'geo': {"lng": 113.390063, "lat": 23.013134},
            'version': '2',
            'source': 'default',
            'client': 'app',
            'previewTime': ''
        })

        params = {
            'appid': 'newtry',
            'uuid': '1623782683334633-4613462616833636',
            'clientVersion': '10.0.2',
            'client': 'wh5',
            'osVersion': '11',
            'functionId': function_id,
            'area': '19_1601_36953_50397',
            'networkType': 'wifi',
            'body': body,
            'ext': {"prstate": "0"},
        }
        url = 'https://api.m.jd.com/client.action' + '?' + urlencode(params)
        response = self.http.post(url)

        return json.loads(response.text)

    def filter_goods(self, item_list):
        """
        筛选商品
        :param item_list:
        :return:
        """
        result = []
        for item in item_list:

            if item.get('applyState', None):  # 已申请
                continue

            if 'tagList' in item and '付费' in str(item['tagList']) or '种草' in str(item['tagList']):
                continue

            if item.get('supplyNum', 1) > self.max_count:
                continue

            price = round(float(item['jdPrice']))
            title = item['skuTitle']
            flag = True

            for key in self.keywords:
                if key in title:
                    flag = False
                    break

            if not flag:
                continue

            if price < self.mini_price:
                continue

            result.append({
                'id': item['trialActivityId'],
                'title': title
            })

        return result

    def get_goods(self, table_id='8', table_name='箱包服饰'):
        """
        :param table_name:
        :param table_id:
        :return:
        """
        goods_list = []
        res = self.request('try_feedsList', {"tabId": table_id, "page": 1, "pageSize": 12})
        if res.get('code', '-1') != '0':
            return []
        data = res.get('data', dict())
        total = data.get('total', 0)
        max_page = 20
        self.print(f'正在获取分类:{table_name}, 共:{max_page}页商品, 商品总数:{total}...')

        item_list = data.get('feedList', list())
        goods_list.extend(self.filter_goods(item_list))

        for page in range(2, max_page + 1):
            self.print('正在获取分类:{}下的商品:{}/{}...'.format(table_name, page, max_page))
            res = self.request('try_feedsList', {"tabId": table_id, "page": page, "pageSize": 12})
            data = res.get('data', dict())
            item_list = data.get('feedList', list())
            if not item_list:
                continue
            goods_list.extend(self.filter_goods(item_list))
            time.sleep(1)

        return goods_list

    def try_goods(self, goods_id):
        """
        :return:
        """
        try:
            url = 'https://api.m.jd.com/client.action'
            body = 'appid=newtry&functionId=try_apply&uuid=1623732683334633-4613462616133636&clientVersion=10.2.2&client=wh5&osVersion=11&area=19_1601_36953_50397&networkType=wifi&body=%7B%22geo%22%3A%7B%22lng%22%3A113.39006%2C%22lat%22%3A23.013134%7D%2C%22activityId%22%3A{}%2C%22previewTime%22%3A%22%22%7D'.format(
                goods_id)

            headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'jdapp;android;10.2.2;11;1623732683334633-4613462616133636;model/RMX2121;addressid/3849226232;aid/a27b83d3d1dba1cc;oaid/;osVer/30;appBuild/91077;partner/oppo;eufv/1;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 11; RMX2121 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045713 Mobile Safari/537.36',
                'referer': 'https://pro.m.jd.com/mall/active/3mpGVQDhvLsMvKfZZumWPQyWt83L/index.html?activityId={}&tttparams=PDq76eyJnTGF0IjoiMjMuMDE1NDExIiwiZ0xuZyI6IjExMy4zODgwOTIiLCJncHNfYXJlYSI6IjE5XzE2MDFfMzY5NTNfNTAzOTciLCJsYXQiOjIzLjAxMzEzNCwibG5nIjoxMTMuMzkwMDYsIm1vZGVsIjoiUk1YMjEyMSIsInByc3RhdGUiOiIwIiwidW5fYXJlYSI6IjE5XzE2MDFfMzY5NTNfNTAzOTcifQ5%3D%3D&lng=113.39006&lat=23.013134&sid=f16bebe609cbc484732f5d188249550w&un_area=19_1601_36953_50397'.format(
                    goods_id),
                'origin': 'https://pro.m.jd.com',

            }
            response = self.http.post(url, data=body, headers=headers)

            data = response.json()

            if data.get('code', '-1') in ['-110', '1']:
                return True
            return False
        except Exception as e:
            self.print('试用商品错误:', e.args)
            return False

    async def run(self):
        for category_name in self.categories:
            category_id = self.tab_map.get(category_name, None)
            if not category_id:
                continue
            goods_list = self.get_goods(category_id, category_name)
            success_num = 0
            fail_num = 0
            if self.success_num >= 300:
                break
            if self.fail_num >= 50:
                break
            self.print(f'开始申请试用分类:《{category_name}》下的{len(goods_list)}个商品:')
            for goods in goods_list:
                success = self.try_goods(goods['id'])
                if success:
                    self.print('成功申请试用商品:《{}》'.format(goods['title']))
                    self.success_num += 1
                    success_num += 1
                else:
                    self.print('无法成功申请试用商品: 《{}》'.format(goods['title']))
                    self.fail_num += 1
                    fail_num += 1
                time.sleep(5)

            self.print('商品分类:{}, 申请成功:{}个, 申请失败:{}个!'.format(category_name, success_num, fail_num))


if __name__ == '__main__':
    run_jd(JdFreeTrial)
