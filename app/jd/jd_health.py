#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_health.py
# @Time    : 2022/4/18 1:17 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 40 7,13,18 * * *
# @Desc    : 东东健康社区
import asyncio
import json
from urllib.parse import urlencode

import aiohttp

from app.jd import JdApp, run_jd

ERRCODE_DEFAULT = 9999


class JdHealth(JdApp):

    def __init__(self, **kwargs):
        super(JdHealth, self).__init__(**kwargs)
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
        return "东东健康"

    async def request(self, session, function_id, body=None, method='POST'):
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
                'client': 'wh5',
                'body': json.dumps(body),
                'clientVersion': '1.0.0',
                'uuid': ''
            }
            url = 'https://api.m.jd.com/?' + urlencode(params)
            if method == 'POST':
                response = await session.post(url=url)
            else:
                response = await session.get(url=url)

            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0:
                return {
                    'bizCode': ERRCODE_DEFAULT,
                    'bizMsg': data['msg']
                }
            else:
                return data['data']

        except Exception as e:
            self.print('获取服务器数据失败:{}!'.format(e.args))
            return {
                'bizCode': ERRCODE_DEFAULT,
                'bizMsg': '获取服务器数据失败!'
            }

    async def get_task_list(self, session):
        """
        获取任务列表
        :return:
        """
        function_id = 'jdhealth_getTaskDetail'
        body = {"buildingId": "", "taskId": "", "channelId": 1}
        res = await self.request(session, function_id, body)
        return res.get('result', dict()).get('taskVos', list())

    async def clockIn(self, session, task):
        """
        早起打卡
        :param session:
        :param task:
        :return:
        """
        function_id = 'jdhealth_collectScore'
        task_token = task['threeMealInfoVos'][0]['taskToken']
        body = {"taskToken": task_token, "taskId": task['taskId'], "actionType": 0}
        res = await self.request(session, function_id, body)
        if res.get('bizCode', ERRCODE_DEFAULT) == 0:
            self.print('打卡成功!')
        else:
            self.print('打卡失败, {}'.format(res.get('bizMsg', '原因未知')))

    async def receive_task(self, session, task_id, task_token):
        """
        领取任务
        :param session:
        :param task_id:
        :param task_token:
        :return:
        """
        function_id = 'jdhealth_collectScore'

        body = {
            'taskId': task_id,
            'taskToken': task_token,
            "actionType": 1,
        }

        return await self.request(session, function_id, body)

    async def receive_task_award(self, session, task_id, task_token):
        """
        领取任务奖励
        :param session:
        :param task_id:
        :param task_token:
        :return:
        """
        function_id = 'jdhealth_collectScore'

        body = {
            'taskId': task_id,
            'taskToken': task_token,
            "actionType": 0,
        }

        return await self.request(session, function_id, body)

    async def browser_task(self, session, task, item_list_key='shoppingActivityVos', task_name=None):
        """
        浏览商品
        :param task_name:
        :param item_list_key:
        :param session:
        :param task:
        :return:
        """
        if not task_name:
            task_name = task.get('taskName')

        task_id = task['taskId']

        item_list = task[item_list_key]

        times, max_times = task['times'], task['maxTimes']

        if times == 0:
            times += 1

        for item in item_list:
            if times > max_times:
                break
            res = await self.receive_task(session, task_id, item['taskToken'])
            self.print('领取任务《{}》{}/{}, {}!'.format(task_name, times, max_times,
                                                res.get('bizMsg')))
            if res.get('bizCode', ERRCODE_DEFAULT) == 105:
                break
            times += 1
            await asyncio.sleep(1)

        timeout = task.get('waitDuration', 1)
        if timeout < 1:
            timeout = 1
        self.print('{}秒后去领取任务《{}》奖励...'.format(timeout, task_name))
        await asyncio.sleep(timeout)

        times, max_times = task['times'], task['maxTimes']

        if times == 0:
            times += 1

        for item in item_list:
            if times > max_times:
                break
            res = await self.receive_task_award(session, task_id, item['taskToken'])
            self.print('领取任务《{}》{}/{}奖励, {}!'.format(task_name,
                                                  times, max_times, res.get('bizMsg')))
            times += 1
            if res.get('bizCode', ERRCODE_DEFAULT) == 105:
                break
            await asyncio.sleep(1)

    async def health_a_bit(self, session):
        """
        健康一下
        :return:
        """
        data = await self.request(session, 'jdhealth_getTaskDetail', {"buildingId": "", "taskId": 22, "channelId": 1})

        status = data.get('result', dict()).get('taskVos',
                                                dict())[-1].get('status', 0)
        if status == 2:
            self.print('健康一下已完成!')
            return

        task_token = data.get('result', dict()).get('taskVos',
                                                    dict())[-1].get('shoppingActivityVos')[-1].get('taskToken', None)
        if not task_token:
            self.print('无法进行健康一下!')
            return

        self.print('正在进行健康一下, 等待6秒!')
        await self.request(session, 'jdhealth_collectScore', {"taskToken": task_token, "taskId": 22, "actionType": 1})
        await asyncio.sleep(6)

        res = await self.request(session, 'jdhealth_collectScore',
                                 {"taskToken": task_token, "taskId": 22, "actionType": 0})

        if res.get('bizCode', ERRCODE_DEFAULT) == 0:
            self.print('完成健康一下!')
        else:
            self.print('无法完成健康一下!')

    async def do_task_list(self, session, task_list):
        """
        做任务
        :param task_list:
        :param session:
        :return:
        """
        for task in task_list:

            task_type, task_name = task.get('taskType'), task.get('taskName')

            if task['status'] == 2:
                self.print('任务《{}》已做完!'.format(task_name))
                continue

            if task_type == 19:  # 下单任务
                self.print('跳过任务:《{}》!'.format(task_name))
                continue
            elif task_type == 10:  # 早起打卡
                await self.clockIn(session, task)
            elif task_type == 9:  # 逛商品
                await self.browser_task(session, task, 'shoppingActivityVos')
            elif task_type == 1:  # 关注店铺
                await self.browser_task(session, task, 'followShopVo')
            elif task_type in [3, 8, 25]:  # 浏览产品
                if 'shoppingActivityVos' in task:
                    await self.browser_task(session, task, 'shoppingActivityVos')
                else:
                    await self.browser_task(session, task, 'productInfoVos')
            else:
                self.print(task_type, task_name)

    async def sign(self, session):
        """
        签到
        :param session:
        :return:
        """
        data = await self.request(session, 'jdhealth_getTaskDetail',
                                  {"buildingId": "", "taskId": 16, "channelId": 1})
        if data.get('bizCode', ERRCODE_DEFAULT) != 0:
            self.print('获取签到数据失败!')
            return

        status = data['result']['taskVos'][-1]['status']

        if status == 2:
            self.print('今日已签到!'.format(self.account))
            return
        task_token = data['result']['taskVos'][-1]['simpleRecordInfoVo']['taskToken']

        sign_params = {"taskToken": task_token, "taskId": 16, "actionType": "0"}

        res = await self.request(session, 'jdhealth_collectScore', sign_params)

        if res.get('bizCode', ERRCODE_DEFAULT) == 0:
            self.print('签到成功!')
        else:
            self.print('签到失败!')

    async def collect_health_energy(self, session):
        res = await self.request(session, 'jdhealth_collectProduceScore')
        if res.get('bizCode', ERRCODE_DEFAULT) != 0:
            self.print('收能量失败!')
        else:
            self.energy = int(res.get('result', dict()).get('userScore', '0'))
            self.print('成功收取能量{}, 当前能量:{}!'.format(
                                                    res.get('result', dict()).get('produceScore'),
                                                    self.energy))

    async def exchange_bean(self, session):
        """
        兑换京豆
        :param session:
        :return:
        """
        res = await self.request(session, 'jdhealth_getCommodities')
        if res.get('bizCode', ERRCODE_DEFAULT) != 0:
            self.print('无法获取可兑换物品列表!'.format(self.account))
            return
        await asyncio.sleep(1)
        item_list = res.get('result', dict()).get('jBeans')

        for i in range(len(item_list)):
            item = item_list[len(item_list) - 1 - i]
            if self.energy < int(item['exchangePoints']):
                continue

            res = await self.request(session, 'jdhealth_exchange',
                                     {"commodityType": item['type'], "commodityId": item['id']})

            if res.get('bizCode', ERRCODE_DEFAULT) == 0:
                self.print('成功兑换{}京豆!'.format(item['title']))
            else:
                self.print('无法兑换{}京豆, {}!'.format(item['title'], res.get('bizMsg', '原因未知')))
                if res.get('bizCode', ERRCODE_DEFAULT) == -6055:  # 到达今日兑换次数上限，不能再兑换哦~
                    break
            await asyncio.sleep(1)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.sign(session)
            for i in range(3):
                task_list = await self.get_task_list(session)
                await self.do_task_list(session, task_list)
            await self.health_a_bit(session)
            await self.collect_health_energy(session)
            await self.exchange_bean(session)


if __name__ == '__main__':
    run_jd(JdHealth)
