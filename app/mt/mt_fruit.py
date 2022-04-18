#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : mt_fruit.py
# @Time    : 2022/4/26 2:03 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    : 美团果园
import asyncio
import base64
import json

import aiohttp
import ujson

from app.mt import MtApp, run_mt
from com.functions import random_string


class MtFruit(MtApp):

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super(MtFruit, self).__init__(**kwargs)
        self.headers = {
            'host': 'mall.meituan.com',
            'origin': 'https://mall.meituan.com',
            't': self.token
        }

    async def get_tasks(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://mall.meituan.com/api/c/mallcoin/game/fruit/task/queryTaskListInfo?' \
              'tenantId=1&poiId=10000013&poi=10000013&bizId=2&utm_medium=iphone&utm_term=5.33.0' \
              '&uuid={}&app_tag=union&userid={}'.format(self.device_id, self.user_id)
        response = await session.get(url)
        data = await response.json()
        return data.get('data', list())

    async def takeTask(self, session, task_id, activity_id):
        """
        :param session:
        :return:
        """
        url = 'https://mall.meituan.com/api/c/mallcoin/game/fruit/task/takeTaskV2?' \
              f'activityId={activity_id}&taskId={task_id}&tenantId=1&' \
              'poiId=10000013&poi=10000013&bizId=2&' \
              'utm_medium=iphone&utm_term=5.33.0&' \
              f'uuid={self.device_id}&app_tag=union&userid={self.user_id}'

        body = {
            "riskMap": {
                "platform": 5,
                "app": 95,
                "fingerprint": base64.b64encode(random_string(64).encode()).decode()
            }
        }

        response = await session.post(url, json=body)

        data = await response.json()

        return data.get('code')

    async def take_task_reward(self, session, reward_id, user_task_id, task_type):
        """
        :param session:
        :return:
        """
        reward_id = 10050
        user_task_id = 333889789
        task_type = 31
        url = 'https://mall.meituan.com/api/c/mallcoin/game/fruit/task/takeTaskReward?' \
              f'rewardId={reward_id}&userTaskId={user_task_id}' \
              f'&taskType={task_type}&tenantId=1&poiId=10000013&poi=10000013&bizId=2&utm_medium=iphone&utm_term=5.33.0' \
              f'&uuid={self.device_id}&app_tag=union&userid={self.user_id}'

        body = {
            "riskMap": {
                "platform": 5,
                "app": 95,
                "fingerprint": base64.b64encode(random_string(64).encode()).decode()
            }
        }
        response = await session.post(url, json=body)

        data = await response.json()

        self.print(data)

    async def water_tree(self, session, tree_id=1503641, count=5):
        """
        :param count:
        :param tree_id:
        :param session:
        :return:
        """
        url = 'https://mall.meituan.com/api/c/mallcoin/game/fruit/waterTreeV2?' \
              f'treeId={tree_id}&preGameInvitedCode=&tenantId=1&poiId=10000013&poi=10000013' \
              '&bizId=2&utm_medium=iphone&utm_term=5.33.0&' \
              f'uuid={self.device_id}&app_tag=union&userid={self.user_id}'
        body = {
            "riskMap": {
                "platform": 5,
                "app": 95,
                "fingerprint": base64.b64encode(random_string(64).encode()).decode()
            }
        }
        for i in range(count):
            response = await session.post(url, json=body)
            data = await response.json()
            self.print(f'第{i+1}浇水结果:', data)
            if data.get('code', -1) != 0:
                break
            await asyncio.sleep(1)

    async def get_tree_info(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://mall.meituan.com/api/c/mallcoin/game/fruit/mainPage?tenantId=1&poiId=10000013' \
              '&poi=10000013&bizId=2&utm_medium=iphone' \
              f'&utm_term=5.33.0&uuid={self.device_id}&app_tag=union&userid={self.user_id}'
        response = await session.get(url)

        data = await response.json()

        return data.get('data', dict())

    @property
    def app_name(self):
        """
        :return:
        """
        return "美团果园"

    async def do_tasks(self, session):
        """
        :param session:
        :return:
        """
        tasks = await self.get_tasks(session)
        for task in tasks:
            task_name = task['taskName']
            if task['buttonDesc'] == '已完成':
                self.print(f'《{task_name}》已完成...')
                continue
            activity_id = task['activityId']
            task_id = task['id']
            await self.takeTask(session, task_id, activity_id)

    async def run(self):
        """

        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, json_serialize=ujson.dumps) as session:
            tree_info = await self.get_tree_info(session)
            tree_id = tree_info['gameTreeInfo']['treeId']
            await self.do_tasks(session)
            await self.water_tree(session, tree_id)


if __name__ == '__main__':
    run_mt(MtFruit)
