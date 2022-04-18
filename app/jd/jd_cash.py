#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_cash.py
# @Time    : 2022/4/18 11:27 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 11 6 * * *
# @Desc    : 签到领现金
import asyncio
import json
from urllib.parse import quote

import aiohttp

from app.jd import JdApp, run_jd


class JdCash(JdApp):

    def __init__(self, **kwargs):

        super(JdCash, self).__init__(**kwargs)
        self.headers.update({
            'Host': 'api.m.jd.com',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Referer': 'https://wq.jd.com/wxapp/pages/hd-interaction/index/index',
        })

    @property
    def app_name(self):
        """
        :return: 
        """
        return "领现金"

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}
        url = 'https://api.m.jd.com/client.action?functionId={}&body={}' \
              '&appid=CashRewardMiniH5Env&clientVersion=9.2.8'.format(function_id, quote(json.dumps(body)))
        try:
            response = await session.get(url=url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            self.print('获取服务器数据失败:{}!'.format(e.args))
            return {
                'code': 9999,
                'data': {
                    'bizCode': 9999
                }
            }

    async def get_task_list(self, session):
        """
        :param session:
        :return:
        """
        try:
            session.headers.add('Host', 'api.m.jd.com')
            session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
            session.headers.add('User-Agent',
                                'okhttp/3.12.1;jdmall;android;version/10.0.6;build/88852;screen/1080x2293;os/11'
                                ';network/wifi;')
            url = 'https://api.m.jd.com/client.action?functionId=cash_homePage&clientVersion=10.0.6&build=88852&client' \
                  '=android&d_brand=realme&d_model=RMX2121&osVersion=11&screen=2293*1080&partner=oppo&oaid=&openudid' \
                  '=a27b83d3d1dba1cc&eid=eidA1a01812289s8Duwy8MyjQ9m/iWxzcoZ6Ig7sNGqHp2V8/mtnOs' \
                  '+KCpWdqNScNZAsDVpNKfHAj3tMYcbWaPRebvCS4mPPRels2DfOi9PV0J+/ZRhX&sdkVersion=30&lang=zh_CN&uuid' \
                  '=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&networkType=wifi&wifiBssid=unknown' \
                  '&uts=0f31TVRjBStRmxA4qmf9RVgENWVO2TGQ2MjkiPwRvZZIAsHZydeSHYcTNHWIbLF17jQfBcdAy' \
                  '%2BSBzhNlEJweToEyKpbS1Yp0P0AKS78EpxJwB8v%2BZSdypE%2BhFoHHlcMyF4pc0QIWs%2B85gCH%2BHp9' \
                  '%2BfP8lKG5QOgoTBOjLn0U5UOXWFvVJlEChArvBygDg6xpmSrzN6AMVHTXrbpV%2FYbl4FQ%3D%3D&uemps=0-0&harmonyOs' \
                  '=0&st=1625744661962&sign=c8b023465a9ec1e9b912ac3f00a36377&sv=110&body={}'.format(
                quote(json.dumps({})))
            response = await session.post(url=url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0 or data['data']['bizCode'] != 0:
                return []
            return data['data']['result']['taskInfos']
        except Exception as e:
            self.print('获取任务列表失败:{}!'.format(e.args))
            return []

    async def get_wx_task_list(self, session):
        """
        获取微信小程序里面的任务
        :param session:
        :return:
        """
        res = await self.request(session, 'cash_mob_home', {"isLTRedPacket": "1"})
        if res['code'] != 0 or res['data']['bizCode'] != 0:
            return []
        return res['data']['result']['taskInfos']

    async def init(self, session):
        """
        获取首页数据
        :return:
        """
        data = await self.request(session, 'cash_mob_home')
        if data['code'] != 0 or data['data']['bizCode'] != 0:
            self.print('初始化数据失败!')
            return False
        return True

    async def do_tasks(self, session, times=4):
        """
        做任务
        :param times:
        :param session:
        :return:
        """
        if times <= 0:
            return

        task_list = await self.get_task_list(session)
        wx_task_list = await self.get_wx_task_list(session)
        task_list.extend(wx_task_list)

        for task in task_list:
            if task['finishFlag'] == 1:
                self.print('任务:《{}》, 今日已完成!'.format(task['name']))
                continue
            if task['type'] == 4:
                task_info = task['jump']['params']['skuId']
            elif task['type'] == 7:
                task_info = 1
            elif task['type'] == 2:
                task_info = task['jump']['params']['shopId']
            elif task['type'] in [16, 3, 5, 17, 21]:
                task_info = task['jump']['params']['url']
            elif task['type'] in [30, 31]:
                task_info = task['jump']['params']['path']
            else:
                self.print('跳过任务:《{}》!'.format(task['name']))
                continue

            self.print('正在进行任务:《{}》, 进度:{}/{}!'.format(task['name'], task['doTimes'], task['times']))
            res = await self.request(session, 'cash_doTask', {
                'type': task['type'],
                'taskInfo': task_info
            })
            await asyncio.sleep(1)

            if res['code'] != 0 or res['data']['bizCode'] != 0:
                self.print('任务:《{}》完成失败, {}!'.format(task['name'], res['data']['bizMsg']))
            else:
                self.print('成功完成任务:《{}》!'.format(task['name']))
        await self.do_tasks(session, times - 1)

    async def get_award(self, session):
        """
        领取奖励
        :param session:
        :return:
        """
        for i in [1, 2]:
            data = await self.request(session, 'cash_mob_reward', {"source": i, "rewardNode": ""})
            if data['code'] != 0 or data['data']['bizCode'] != 0:
                self.print('领取奖励失败!')
            else:
                self.print('成功领取奖励!')
            await asyncio.sleep(2)

    async def sign(self, session):
        """
        签到
        :param session:
        :return:
        """
        try:
            url = 'https://api.m.jd.com/client.action?functionId=cash_sign&clientVersion=10.0.11&build=89314&client' \
                  '=android&osVersion=11&partner=jingdong&openudid=a27b83d3d1dba1cc&sdkVersion=30&uuid=a27b83d3d1dba1cc' \
                  '&aid=a27b83d3d1dba1cc&networkType=wifi&st=1628419999801&sign=9c2543218680da1f16e0a36afb8c5ba1&sv=100' \
                  '&body=%7B%22breakReward%22%3A0%2C%22inviteCode%22%3Anull%2C%22remind%22%3A0%2C%22type%22%3A0%7D&'
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            self.print('签到结果;{}!'.format(data['data']['bizMsg']))
        except Exception as e:
            self.print('签到异常, {}'.format(e.args))

    async def withdraw_ten(self, session):
        """
        提现10元
        :return:
        """
        try:
            url = 'https://api.m.jd.com/client.action?functionId=cash_wx_withdraw&clientVersion=10.0.11&build=89314' \
                  '&client=android&screen=2293*1080&partner=jingdong&oaid=&openudid=a27b83d3d1dba1cc&sdkVersion=30' \
                  '&lang=zh_CN&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&networkType=wifi&st=1628420578663&sign' \
                  '=9dc459ed7419420373445f67bbd6c12b&sv=122&body=%7B%22amount%22%3A1000%2C%22code%22%3A%22001nc' \
                  'QFa1THZwB0muVFa16WXOe0ncQFm%22%7D&'
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            self.print('{}, 提现10元结果{}!'.format(self.account, data['data']['bizMsg']))
        except Exception as e:
            self.print('{}, 提现10元异常, {}'.format(self.account, e.args))

    async def run(self):
        """
        入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            success = await self.init(session)
            if not success:
                self.print('{}, 无法初始化数据, 退出程序!'.format(self.account))
                return
            await self.sign(session)
            await self.do_tasks(session)
            await self.withdraw_ten(session)


if __name__ == '__main__':
    run_jd(JdCash)
