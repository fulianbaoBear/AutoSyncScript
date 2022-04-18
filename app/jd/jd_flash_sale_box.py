#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_flash_sale_box.py.py
# @Time    : 2022/4/18 12:21 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 8 8 * * *
# @Desc    : 闪购盲盒
import asyncio
import json
from urllib.parse import urlencode

import aiohttp

from app.jd import JdApp, run_jd


class JdFlashSaleBox(JdApp):

    def __init__(self, **kwargs):

        super(JdFlashSaleBox, self).__init__(**kwargs)
        self.headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://h5.m.jd.com',
            'referer': 'https://h5.m.jd.com/',
        })

    @property
    def app_name(self):
        """
        :return:
        """
        return "闪购盲盒"

    async def request(self, session, function_id, body=None, method='GET'):
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
            url = 'https://api.m.jd.com/client.action?'
            params = {
                'functionId': function_id,
                'body': json.dumps(body),
                'client': 'wh5',
                'clientVersion': '1.0.0'
            }
            url += urlencode(params)

            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)

            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            self.print('获取服务器数据失败:{}!'.format(e.args))
            return {
                'code': 9999
            }

    async def do_task(self, session, task):
        """
        做任务
        :param session:
        :param task:
        :return:
        """
        do_times = task['times']  # 已经完成的次数
        max_times = task['maxTimes']
        task_name = task['taskName']
        task_id = task['taskId']
        if do_times >= max_times:
            self.print('任务《{}》已完成!'.format(task_name))
            return

        if 'waitDuration' in task and task['waitDuration'] > 0:
            timeout = task['waitDuration']
        else:
            timeout = 2

        if 'productInfoVos' in task:
            item_list = task['productInfoVos']
        elif 'browseShopVo' in task:
            item_list = task['browseShopVo']
        elif 'shoppingActivityVos' in task:
            item_list = task['shoppingActivityVos']
        else:
            item_list = []

        for item in item_list:
            if do_times > max_times:
                break
            body = {
                "appId": "1EFRXxg",
                "taskToken": item['taskToken'],
                "taskId": task_id,
                "actionType": 1
            }
            res = await self.request(session, 'harmony_collectScore', body)
            if res['code'] == 0:
                self.print('任务:《{}》,{}!'.format(task_name, res['data']['bizMsg']))
            else:
                self.print('任务:{}领取失败!'.format(task_name))

            self.print('正在做任务:{}, 等待{}秒!'.format(task_name, timeout))
            await asyncio.sleep(timeout)

            body = {
                "appId": "1EFRXxg",
                "taskToken": item['taskToken'],
                "taskId": task_id,
                "actionType": 0
            }
            res = await self.request(session, 'harmony_collectScore', body)
            if res['code'] != 0:
                continue
            self.print('{}!'.format(res['data']['bizMsg']))
            do_times += 1


    async def do_tasks(self, session):
        """
        :param session:
        :return:
        """
        res = await self.request(session, 'healthyDay_getHomeData', {"appId":"1EFRXxg","taskToken":"","channelId":1})
        if res['code'] != 0 or res['data']['bizCode'] != 0:
            self.print('获取任务列表失败!'.format(self.account))
            return

        data = res['data']['result']
        task_list = data['taskVos']

        for task in task_list:
            task_name, task_type = task['taskName'], task['taskType']
            if task_type == 14:   # 邀请好友助力
                continue
            await self.do_task(session, task)

    async def lottery(self, session):
        """
        抽奖
        :param session:
        :return:
        """
        self.print('正在查询抽奖次数!')
        res = await self.request(session, 'healthyDay_getHomeData',
                                 {"appId": "1EFRXxg", "taskToken": "", "channelId": 1})
        if res['code'] != 0 or res['data']['bizCode'] != 0:
            self.print('查询抽奖次数失败!')
            return

        times = int(res['data']['result']['userInfo']['lotteryNum'])

        if times < 1:
            self.print('当前已无抽奖次数!')
            return

        self.print('当前有{}次抽奖机会, 开始抽奖!'.format(times))

        for i in range(1, times+1):
            await asyncio.sleep(1)
            res = await self.request(session, 'interact_template_getLotteryResult', {"appId": "1EFRXxg"})
            if res['code'] != 0 or res['data']['bizCode'] != 0:
                self.print('第{}次抽奖失败, 退出抽奖'.format(i))
                break
            if res['data']['result']['userAwardsCacheDto']['type'] == 0:
                self.print('第{}次抽奖, 未抽中奖励!'.format(i))
            elif res['data']['result']['userAwardsCacheDto']['type'] == 2:
                self.print('第{}次抽奖, 获得{}'.format(i,
                        res['data']['result']['userAwardsCacheDto']['jBeanAwardVo']['prizeName']))
            else:
                self.print('第{}次抽奖, 获得奖励未知~'.format( i))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            await self.do_tasks(session)
            await self.lottery(session)


if __name__ == '__main__':
    run_jd(JdFlashSaleBox)
