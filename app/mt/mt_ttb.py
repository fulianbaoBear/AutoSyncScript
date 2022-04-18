#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : mt_ttb.py
# @Time    : 2022/4/20 1:47 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 22 3,4,5 * * *
# @Desc    : 赚团团币
import base64
import urllib.parse
import aiohttp
import requests
from app.mt import MtApp, run_mt


class MtGroupCoins(MtApp):

    def __init__(self, **kwargs):

        super(MtGroupCoins, self).__init__(**kwargs)

        access_token = self.get_access_token()

        self.headers.update({"acToken": access_token, "accessToken": self.token})

    @property
    def app_name(self):
        return "赚团团币"

    def get_access_token(self):
        """
        :return:
        """
        url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/login'
        params = {
            "mtToken": self.token,
            "deviceUUID": self.device_id,
            "mtUserId": self.user_id,
            "idempotentString": "d7s7tozhqeifz0dh"
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/15.3.1 meituangroup/com.meituan.imeituan/11.19.205 meituangroup/11.19.205 App/10110/11.19.205 iPhone/iPhone13Pro WKWebView EH/8.3.0 EHSkeleton/1',
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://mgc.meituan.com/',
            'origin': 'https://mgc.meituan.com',
        }
        response = requests.post(url, json=params, headers=headers)

        data = response.json()
        try:

            return data.get('data', dict()).get('loginInfo', dict()).get('accessToken', '')
        except Exception as e:
            self.print(f'获取access token失败:{e.args}, ', data)
            return ''

    async def get_task_list(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/queryMgcTaskInfo?externalStr' \
              '=&riskParams='
        response = await session.get(url)
        data = await response.json()

        if data.get('code', -1) == 0:
            return data['data']['taskList']
        else:
            self.print('获取任务列表失败:', data)
            return []

    async def get_game_list(self, session):
        """
        获取小游戏列表
        :param session:
        :return:
        """
        url = 'https://game.meituan.com/mgc/gamecenter/entryResource/index?cityId=20&pt=iphone&version=11.19.205' \
              '&encryptLatlng=01q!q&uuid=' + self.device_id
        response = await session.get(url)
        data = await response.json()

        game_list = []
        if data.get('code', -1) == 0:
            for item in data['data'].values():
                game_list.extend(item)
            return game_list
        else:
            return []

    async def do_task(self, session, task):
        """
        做任务
        :param session:
        :param task:
        :return:
        """
        task_name = task['mgcTaskBaseInfo']['viewTitle']
        task_status = task['status']

        if task_status == 4:
            self.print(f'任务:《{task_name}》今日已完成...')
            return

        params = {
            'taskId': base64.b64encode('mgc-gamecenter{}'.format(str(task['id'])).encode()),
            'externalStr': '',
            'riskParams': '',
        }
        if task_status == 3:
            url = 'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/receiveMgcTaskRewardV2?' \
                  'taskId={}&externalStr=&riskParams='.format(task['id'])
        else:
            url = 'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/finishAndReceiveReward?' + urllib.parse.urlencode(
                params)

        response = await session.get(url)

        data = await response.json()

        if data.get('code', -1) == 0:
            self.print(f'成功完成任务:《{task_name}》...')
        else:
            self.print(f'无法完成任务:《{task_name}》, ', data)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            task_list = await self.get_task_list(session)
            for task in task_list:
                await self.do_task(session, task)


if __name__ == '__main__':
    run_mt(MtGroupCoins)
