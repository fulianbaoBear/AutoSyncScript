#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : mt_make_money.py
# @Time    : 2022/4/20 5:55 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 48 7 * * *
# @Desc    :
import asyncio
import base64

import aiohttp
import requests
import ujson

from app.mt import MtApp, run_mt
from com.functions import random_string


class MtMakeMoney(MtApp):

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super(MtMakeMoney, self).__init__(**kwargs)
        self.access_token = self.get_access_token()
        self.headers.update({
            'actoken': self.access_token
        })

    def get_access_token(self):
        """
        :return:
        """
        url = 'https://game.meituan.com/mgc/gamecenter/sign/login'
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/15.3.1 meituangroup/com.meituan.imeituan/11.19.205 meituangroup/11.19.205 App/10110/11.19.205 iPhone/iPhone13Pro WKWebView EH/8.3.0 EHSkeleton/1',
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://mgc.meituan.com/',
            'origin': 'https://mgc.meituan.com',
        }
        params = {
            "mtUserId": self.user_id,
            "mtDeviceId": self.device_id[14:],
            "mtToken": self.token,
            "nonceStr": "yvq0vtuo58qs3dmz",
            "externalStr": {"cityId": "20"}
        }
        response = requests.post(url=url, json=params, headers=headers)

        data = response.json()
        if data.get('code', None) != 0:
            return ''
        return data.get('data', dict()).get('loginAccountResponse', dict()).get('accessToken', '')

    async def get_task_list(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/queryMgcTaskInfo?externalStr=&riskParams='
        response = await session.get(url)
        data = await response.json()

        if data.get('code', -1) == 0:
            return data['data']['taskList']
        else:
            self.print('获取任务列表失败:', data)
            return []

    async def update_push_status(self, session, status=0):
        """
        更新推送
        :param session:
        :param status:
        :return:
        """
        url = 'https://game.meituan.com/mgc/gamecenter/sign/updatePushStatus'
        params = {
            "accessToken": self.access_token,
            "pushType": status
        }
        response = await session.post(url, json=params)
        data = await response.json()
        return data.get('code', None) == 0

    async def do_task(self, session, task):
        """
        :param session:
        :param task:
        :return:
        """

        task_name = task['mgcTaskBaseInfo']['viewTitle']
        task_status = task['status']

        if task_status == 4:
            self.print(f'任务:《{task_name}》今日已完成...')
            return

        if '下单' in task_name or '转新任务' in task_name:
            return

        if task_status == 3:
            url = 'https://game.meituan.com/mgc/gamecenter/sign/receiveMgcTaskReward'
        else:
            url = 'https://game.meituan.com/mgc/gamecenter/sign/finishMgcTaskAndReceiveReward'
        params = {
            "accessToken": self.access_token,
            "taskId": task['id'],
            "riskParam": {
                "ip": "",
                "uuid": self.device_id,
                "platform": 5,
                "version": "11.19.205",
                "app": 0,
                "fingerprint": base64.b64encode(random_string(64).encode()).decode()
            }
        }
        response = await session.post(url=url, json=params)
        data = await response.json()
        if data.get('code', None) != 0:
            self.print(f'无法完成任务:《{task_name}》, 原因:', data.get('msg', '未知').strip())
        else:
            self.print(f'成功完成任务:《{task_name}》...')

    @property
    def app_name(self):
        """
        :return:
        """
        return "点点就有钱"

    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        task_list = await self.get_task_list(session)

        for task in task_list:
            await self.do_task(session, task)

    async def run(self):

        async with aiohttp.ClientSession(headers=self.headers, json_serialize=ujson.dumps) as session:
            await self.update_push_status(session, 2)  # 开启推送
            for i in range(5):
                await self.do_tasks(session)
                await asyncio.sleep(2)
            await self.update_push_status(session, 0)  # 关闭推送


if __name__ == '__main__':
    run_mt(MtMakeMoney)

