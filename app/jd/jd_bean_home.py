#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_bean_home.py
# @Time    : 2022/4/18 11:10 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 5 12 * * *
# @Desc    : 京豆签到/领额外京豆
import asyncio
import json
from urllib.parse import urlencode

import aiohttp

from app.jd import JdApp, run_jd
from com.functions import random_integer_string


class JdBeanHome(JdApp):

    def __init__(self, **kwargs):
        super(JdBeanHome, self).__init__(**kwargs)
        self.headers.update({
            'referer': 'https://h5.m.jd.com/rn/2E9A2bEeqQqBP9juVgPJvQQq6fJ/index.html',
        })
        self.eu = random_integer_string(16)
        self.fv = random_integer_string(16)

    @property
    def app_name(self):
        return "京豆签到/领额外京豆"

    async def request(self, session, function_id='', body=None, method='GET'):
        """
        请求数据
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        try:
            if not body:
                body = {}
            params = {
                'functionId': function_id,
                'appid': 'ld',
                'clientVersion': '10.0.11',
                'client': 'apple',
                'eu': self.eu,
                'fv': self.fv,
                'osVersion': 11,
                'uuid': self.eu + self.fv,
                'openudid': self.eu + self.fv,
                'body': json.dumps(body)
            }
            url = 'https://api.m.jd.com/client.action?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)

            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            self.print(f'请求服务器错误:{e.args}')
            return {
                'code': 999
            }

    async def get_award(self, session, source='home'):
        """
        领取奖励
        :param source: 来源
        :param session:
        :return:
        """
        res = await self.request(session, 'beanHomeTask', {"source": source, "awardFlag": True})
        if res['code'] == '0' and 'errorCode' not in res:
            self.print('领取京豆奖励, 获得京豆:{}!'.format(res['data']['beanNum']))
        else:
            message = res.get('errorMessage', '未知')
            self.print('领取京豆奖励失败, {}!'.format(message))

        await asyncio.sleep(2)

    async def do_task(self, session):
        """
        :param session:
        :return:
        """
        res = await self.request(session, 'findBeanHome',
                                 {"source": "wojing2", "orderId": 'null', "rnVersion": "3.9", "rnClient": "1"})
        if res['code'] != '0':
            self.print('获取首页数据失败!')
            return False

        if res['data']['taskProgress'] == res['data']['taskThreshold']:
            self.print('今日已完成领额外京豆任务!')
            return

        for i in range(1, 6):
            body = {"type": str(i), "source": "home", "awardFlag": False, "itemId": ""}
            res = await self.request(session, 'beanHomeTask', body)
            if res['code'] == '0' and 'errorCode' not in res:
                self.print('领额外京豆任务进度:{}/{}!'.format(res['data']['taskProgress'],
                                                     res['data']['taskThreshold']))
            else:
                message = res.get('errorMessage', '原因未知')
                self.print('第{}个领额外京豆任务完成失败, {}!'.format(i, message))
            await asyncio.sleep(2)

    async def do_goods_task(self, session):
        """
        浏览商品任务
        :return:
        """
        res = await self.request(session, 'homeFeedsList', {"page": 1})
        if res['code'] != '0' or 'errorCode' in res:
            self.print('无法浏览商品任务!')

        if res['data']['taskProgress'] == res['data']['taskThreshold']:
            self.print('今日已完成浏览商品任务!')
            return

        await asyncio.sleep(2)

        for i in range(3):
            body = {
                "skuId": str(random.randint(10000000, 20000000)),
                "awardFlag": False,
                "type": "1",
                "source": "feeds",
                "scanTime": int(time.time() * 1000)
            }
            res = await self.request(session, 'beanHomeTask', body)
            if 'errorCode' in res:
                self.print('浏览商品任务, {}!'.format(res.get('errorMessage', '原因未知')))
                if res['errorCode'] == 'HT203':
                    break
            else:
                self.print(' 完成浏览商品任务, 进度:{}/{}!'.format(res['data']['taskProgress'],
                                                         res['data']['taskThreshold']))
            await asyncio.sleep(2)

    async def bean_sign(self, session):
        """
        领京豆-签到
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=signBeanIndex&body=%7B%22monitor_refer%22%3A%22%22%2C' \
              '%22rnVersion%22%3A%223.9%22%2C%22fp%22%3A%22-1%22%2C%22shshshfp%22%3A%22-1%22%2C%22shshshfpa%22%3A%22' \
              '-1%22%2C%22referUrl%22%3A%22-1%22%2C%22userAgent%22%3A%22-1%22%2C%22jda%22%3A%22-1%22%2C' \
              '%22monitor_source%22%3A%22bean_m_bean_index%22%7D&appid=ld&client=apple&clientVersion=10.0.11' \
              '&networkType=wifi&osVersion=14&uuid=1623732683334633-4613462616133636&eu=1623732683334633&fv' \
              '=4613462616133636&jsonp='

        response = await session.post(url)
        res = await response.text()
        res = json.loads(res)

        if res.get('code', '-1') != '0':
            self.print('签到失败!')
            return

        status = int(res.get('data', dict()).get('status', '-1'))

        if status == 1:
            self.print('签到成功!')

        elif status == 2:
            self.print('今日已签到!')

        else:
            self.print('签到失败!')

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.bean_sign(session)
            await self.do_task(session)
            await self.get_award(session)
            await self.do_goods_task(session)
            await self.get_award(session, source='feeds')


if __name__ == '__main__':
    run_jd(JdBeanHome)
