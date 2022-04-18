#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : mt_egg.py
# @Time    : 2022/4/21 1:40 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 35 5,7,13,17,23 * * *
# @Desc    : 天天领鸡蛋
import asyncio
import aiohttp
import ujson

from app.mt import MtApp, run_mt


class MtEgg(MtApp):

    def __init__(self, **kwargs):
        super(MtEgg, self).__init__(**kwargs)
        self.headers = {
            'user-agent': 'imeituan/11.19.205 (iPhone; iOS 15.3.1; Scale/3.00)',
            'ce-activity-id': '2000013',
            't': self.token
        }

    @property
    def app_name(self):
        """
        :return:
        """
        return "天天领鸡蛋"

    async def request(self, session, url, data=None, method='GET'):
        """
        :param session:
        :param url:
        :param data:
        :param method:
        :return:
        """
        if not data:
            data = {}
        if method == 'GET':
            response = await session.get(url)
        else:
            response = await session.post(url, json=data)

        res = await response.json()

        if res.get('code', -1) == 0:
            return res.get('data', dict())
        else:
            return res

    async def process(self, session, task_config_id, task_type):
        """
        :param session:
        :param task_config_id:
        :param task_type:
        :return:
        """
        url = 'https://grocery-game.meituan.com/api/c/game/collect/eggs/task/process?' \
              'poi=0&poiIdStr=2k7PiSt38QusLm_OjkbVWgE&utm_medium=tuanApp&utm_term=5.89.8&' \
              'ci=4&fp_user_id={}&taskType={}&userTaskId=&taskConfigId={}'.format(self.user_id, task_type, task_config_id)

        body = {
            "uuid": self.device_id,
            "platform": 20,
            "appletsFingerprint": "",
            "fingerprint": "",
            "h5Fingerprint": "",
            "wxRiskLevel": "{\"openId\":\"\",\"appId\":\"mgcy6fu5rxcvqnhf\",\"mchid\":\"1399386702\"}",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E8301 MicroMessenger/6.6.0 MiniGame NetType/WIFI Language/zh_CN",
            "version": "11.19.205",
            "app": 0,
            "openId": "",
            "openIdCipher": "",
            "riskUuid": self.device_id
        }

        res = await self.request(session, url, body, 'POST')

        return res.get('code', -1) == 0

    async def take_award(self, session, user_task_id, task_config_id, task_type):
        """
        :param session:
        :return:
        """
        url = 'https://grocery-game.meituan.com/api/c/game/collect/eggs/task/take_rewards' \
              '?poi=0&poiIdStr=2k7PiSt38QusLm_OjkbVWgE&utm_medium=tuanApp&utm_term=5.89.8&ci=4' \
              '&fp_user_id={}&userTaskId={}&taskConfigId={}&taskType={}'. \
            format(self.user_id, user_task_id, task_config_id, task_type)

        body = {
            "uuid": self.device_id,
            "platform": 20,
            "appletsFingerprint": "",
            "fingerprint": "",
            "h5Fingerprint": "",
            "wxRiskLevel": "{\"openId\":\"\",\"appId\":\"mgcy6fu5rxcvqnhf\",\"mchid\":\"1399386702\"}",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E8301 MicroMessenger/6.6.0 MiniGame NetType/WIFI Language/zh_CN",
            "version": "11.19.205",
            "app": 0,
            "openId": "",
            "openIdCipher": "",
            "riskUuid": self.device_id
        }

        res = await self.request(session, url, body, 'POST')

        return res.get('code', -1) == 0

    async def feed(self, session):
        """
        喂食
        :param session:
        :return:
        """
        url = 'https://grocery-game.meituan.com/api/c/game/collect/eggs/raise/feed' \
              '?poi=0&poiIdStr=2k7PiSt38QusLm_OjkbVWgE&' \
              'utm_medium=mtApp&utm_term=5.89.8&ci=4&fp_user_id={}'.format(self.user_id)

        body = {
            "uuid": self.device_id,
            "platform": 20,
            "appletsFingerprint": "",
            "fingerprint": "",
            "h5Fingerprint": "",
            "wxRiskLevel": "{\"openId\":\"\",\"appId\":\"mgcy6fu5rxcvqnhf\",\"mchid\":\"1399386702\"}",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E8301 MicroMessenger/6.6.0 MiniGame NetType/WIFI Language/zh_CN",
            "version": "11.19.205",
            "app": 0,
            "openId": "",
            "openIdCipher": "",
            "riskUuid": self.device_id
        }

        for i in range(10):
            res = await self.request(session, url, body, 'POST')
            if res.get('code', -1) == 0:
                self.print('成功投喂一次小🐔...')
            else:
                self.print('投喂小🐔失败, {}...'.format(res.get('error', dict()).get('msg', '未知')))
                break
            await asyncio.sleep(1)

    async def collect(self, session):
        """
        收鸡蛋
        :return:
        """
        url = 'https://grocery-game.meituan.com/api/c/game/collect/eggs/raise/collect?poi=0&' \
              'poiIdStr=a2Df_7E8CEUyJmW7KQ7SrAE&utm_medium=wxapp&utm_term=5.91.11&ci=4&fp_user_id={}'.format(self.user_id)
        body = {
            "uuid": self.device_id,
            "platform": 20,
            "appletsFingerprint": "",
            "fingerprint": "",
            "h5Fingerprint": "",
            "wxRiskLevel": "{\"openId\":\"\",\"appId\":\"mgcy6fu5rxcvqnhf\",\"mchid\":\"1399386702\"}",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E8301 MicroMessenger/6.6.0 MiniGame NetType/WIFI Language/zh_CN",
            "version": "11.19.205",
            "app": 0,
            "openId": "",
            "openIdCipher": "",
            "riskUuid": self.device_id
        }

        res = await self.request(session, url, body, 'POST')
        self.print('收鸡蛋:', res)

    async def do_tasks(self, session):
        """
        :param session:
        :return:
        """
        get_task_url = 'https://grocery-game.meituan.com/api/c/game/collect/eggs/task/list?' \
                       'poi=0&poiIdStr=2k7PiSt38QusLm_OjkbVWgE&utm_medium=tuanApp&utm_term=5.89.8' \
                       '&ci=4&fp_user_id={}'.format(self.user_id)
        task_data = await self.request(session, get_task_url)

        task_list = task_data.get('ceTaskDTOList', [])

        for task in task_list:
            task_name = task['name']
            task_status = task['taskStatus']
            current_status = task['currentStatus']
            task_type = task['taskType']
            task_config_id = task['taskConfigId']

            if task_status == 2 or current_status == 2:
                self.print(f'已完成任务:《{task_name}》...')
                continue
            if '下单' in task_name or '邀请' in task_name or '助力' in task_name:
                continue

            if current_status == 3 or task_status == 3:
                user_task_id = task['newUserTaskId']
                b = await self.take_award(session, user_task_id, task_config_id, task_type)
                if b:
                    self.print(f'成功领取任务:《{task_name}》奖励...')
                else:
                    self.print(f'无法领取任务:《{task_name}》奖励...')
                await asyncio.sleep(1)
                continue

            b = await self.process(session, task_config_id, task_type)
            if b:
                self.print(f'成功完成任务:{task_name}...')
            else:
                self.print(f'无法完成任务:{task_name}...')

            await asyncio.sleep(1)

    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers, json_serialize=ujson.dumps) as session:
            await self.do_tasks(session)
            await self.feed(session)
            await self.collect(session)


if __name__ == '__main__':
    run_mt(MtEgg)
