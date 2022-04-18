#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : elm.py
# @Time    : 2022/4/19 6:05 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 0 7,10 * * *
# @Desc    : 饿了么刷吃货豆
import asyncio
import random
import aiohttp
from rich.console import Console
from conf.config import ELM_CONF


class Elm:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        self.sid = kwargs.get('sid', None)
        if not self.sid:
            raise ValueError('sid is required.')

        self.headers = {
            'user-agent': 'Rajax/1 Apple/iPhone14,2 iOS/15.3.1 Eleme/10.7.5 ID/8A4C95DA-E091-46C6-8042-D6C1CB45D4B7;'
                          ' IsJailbroken/0 ASI/144ACF6C-68EC-4A49-9FEC-3B1BFDCFDFD5 Mozilla/5.0'
                          ' (iPhone; CPU iPhone OS 15_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                          'Mobile/15E148 AliApp(ELMC/10.7.5) UT4Aplus/ltracker-0.0.6 WindVane/8.7.2 1170x2532 WK',
            'referer': 'https://h5.ele.me/svip/task-list?spm=a2ogi.15080242.moretask.1',
            'content-type': 'application/json, text/plain, */*',
        }
        self.longitude = str(random.uniform(113, 115))
        self.latitude = str(random.uniform(22, 24))
        self.user_id = None
        self.console = Console()

    def print(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        style = kwargs.get('style', 'bold red')
        kwargs['style'] = style
        self.console.print(f'用户{self.user_id}):', *args, **kwargs)

    async def get_user_id(self, session):
        """
        获取用户ID
        :param session:
        :return:
        """
        url = 'https://h5.ele.me/restapi/eus/v2/current_user_with_havana'
        response = await session.get(url)
        data = await response.json()
        self.user_id = data.get('userId', -1)

    async def receive_elm_bean(self):
        """
        :return:
        """

        url = 'https://h5.ele.me/restapi/biz.svip_scene/svip/engine/xSupply'
        data = {
            "params": [{
                "tagCode": "427048",
                "extra": {
                    "solutionType": "RECEIVE_PRIZE",
                    "phaseId": 233,

                    "actId": "20210826153802420194984542",
                    "sceneCode": "divide_chd_interact",
                    "amount": 36
                }
            }],
            "bizCode": "biz_card_main",
            "longitude": self.longitude,
            "latitude": self.latitude
        }

    async def get_task_list(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://h5.ele.me/restapi/biz.svip_scene/svip/engine/queryTrafficSupply?tagParams%5B%5D=%7B%22tagCode' \
              '%22%3A%22224166%22%7D&bizCode=biz_card_main&longitude={}&latitude={}'.format(self.longitude,
                                                                                            self.latitude)
        response = await session.get(url)
        res = await response.json()
        if res.get('code', '-1') != '200':
            self.print('获取任务列表失败...')
            return

        try:
            data = res.get('data')[0]['data']
            return data
        except Exception as e:
            self.print(f'获取任务列表失败, {e.args}')
            return []

    async def join(self, session):
        """
        参与瓜分吃货豆
        :param session:
        :return:
        """
        url = 'https://h5.ele.me/restapi/biz.svip_scene/svip/engine/xSupply?asac=2A21810EF0RWWEQDVS7SL6'
        body = {
            "params": [{
                "tagCode": "381410",
                "extra": {
                    "solutionType": "ENROLL",
                    "phaseId": 235,
                    "actId": "20210826153802420194984542",
                    "sceneCode": "divide_chd_interact",
                    "client": "eleme"
                }
            }],
            "bizCode": "biz_card_main",
            "longitude": self.longitude,
            "latitude": self.latitude
        }
        response = await session.post(url, json=body)
        res = await response.json()
        self.print('参与瓜分吃货豆结果:', res)

    async def receive_award(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://h5.ele.me/restapi/biz.svip_scene/svip/engine/queryTrafficSupply?tagParams=[%7B%22tagCode%22:%22347079%22,%22extra%22:%7B%22solutionType%22:%22QUERY%22,%22actId%22:%2220210826153802420194984542%22,%22sceneCode%22:%22divide_chd_interact%22,%22client%22:%22eleme%22%7D%7D]&bizCode=biz_card_main' \
              '&longitude={}&latitude={}'.format(self.longitude, self.latitude)
        response = await session.get(url)
        res = await response.json()
        if res.get('code', None) != '200':
            return
        data = res['data'][0]['data'][0]['attribute']

        if not data['isToReceive']:
            self.print('暂时无法领取瓜分吃货豆奖励...')
            return

        url = 'https://h5.ele.me/restapi/biz.svip_scene/svip/engine/xSupply'
        body = {
            "params": [{
                "tagCode": "427048",
                "extra": {
                    "solutionType": "RECEIVE_PRIZE",
                    "phaseId": data['curPhaseId'],
                    "actId": "20210826153802420194984542",
                    "sceneCode": "divide_chd_interact",
                    "amount": data['lastPrizeInfo']['amount']
                }
            }],
            "bizCode": "biz_card_main",
            "longitude": self.longitude,
            "latitude": self.latitude
        }
        response = await session.post(url, json=body)
        res = await response.json()
        self.print('领取瓜分吃货豆奖励结果:', res)

    async def do_task(self, session, task):
        """
        :param task:
        :param session:
        :return:
        """
        task_name = task['showTitle']
        if task['rewardStatus'] == 'SUCCESS' or task['missionType'] == 'PAGEVIEW':
            self.print(f'{task_name} 已完成...')
            return

        if task['missionType'] == 'THIRD':
            return

        url = "https://h5.ele.me/restapi/biz.svip_scene/svip/engine/xSupply?params[]=%7B%22tagCode%22:%22223166%22," \
              "%22extra%22:%7B%22missionDefId%22:{},%22missionCollectionId%22:{}," \
              "%22missionType%22:%22{}%22%7D%7D&bizCode=biz_code_main&longitude={}&latitude" \
              "={}".format(task['missionDefId'], task['missionCollectionId'], task['missionType'], self.longitude,
                           self.latitude)
        response = await session.get(url)
        res = await response.json()
        if res.get('code', '-100') == '200' and res['data'][0]['attribute']['msgCode'] == '0':
            self.print(f'成功完成任务：《{task_name}》...')
        else:
            self.print(f'无法完成任务:《{task_name}》, ', res)

        # if task['missionType'] == 'PAGEVIEW':
        #     url = task['missionActionUrl'] +'?missioncollectid={}&missionid={}&taskfrom={}&' \
        #                                     'bizscene=svip&taskpageviewasac=2A21119A45TTVAEXP40N7N&' \
        #                                     'spm=a2ogi.chihuo_home_tasklist.tasklayer_scantask.{}'.format(task['missionCollectionId'], task['missionDefId'], task['pageSpm'], task['finalStageCount'])
        #     await session.get(url)
        #     self.print(f'任务:《{task_name}》进行中, 等待15s...')
        #     await asyncio.sleep(15.1)

    async def query(self, session):
        """
        查询吃货豆
        :return:
        """
        url = 'https://h5.ele.me/restapi/biz.svip_bonus/v1/users/supervip/pea/queryAccountBalance?' \
              'types=[%22PEA_ACCOUNT%22]&longitude={}&latitude={}'.format(self.longitude, self.latitude)
        response = await session.get(url)
        res = await response.json()
        cnt = -1
        for item in res.get('accountInfos', list()):
            if item['balanceType'] == 'PEA_ACCOUNT':
                cnt = item['count']

        if cnt == -1:
            self.print('查询吃货豆失败...')
        else:
            self.print(f'当前吃货豆:{cnt}')

    async def receive_task(self, session):
        """
        :param session:
        :return:
        """


    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies={'SID': self.sid}) as session:
            await self.get_user_id(session)
            task_list = await self.get_task_list(session)
            for task in task_list:
                await self.do_task(session, task['attribute'])
            await self.receive_award(session)
            await self.join(session)
            await self.receive_task(session)
            await self.query(session)


def start():
    """
    :return:
    """
    sid_list = ELM_CONF.get('sid', None)
    if not sid_list:
        print('未配置饿了么cookies, 无法执行程序...')
        return
    for sid in sid_list:
        app = Elm(sid=sid)
        asyncio.run(app.run())


if __name__ == '__main__':
    start()
