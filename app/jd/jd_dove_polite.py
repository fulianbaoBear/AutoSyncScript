#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_dove_polite.py
# @Time    : 2022/4/18 1:58 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 10 10 * * *
# @Desc    : 小鸽有礼
import asyncio
import json

import aiohttp

from app.jd import JdApp, run_jd


class JdDovePolite(JdApp):

    def __init__(self, **kwargs):
        super(JdDovePolite, self).__init__(**kwargs)
        self.headers.update({
            'origin': 'https://jingcai-h5.jd.com',
            'lop-dn': 'jingcai.jd.com',
            'accept': 'application/json, text/plain, */*',
            'appparams': '{"appid":158,"ticket_type":"m"}',
            'content-type': 'application/json',
            'referer': 'https://jingcai-h5.jd.com/index.html'
        })
        self.activityCode = "1410048365793640448"

    @property
    def app_name(self):
        return "小鸽有礼"
    
    async def request(self, session, path, body=None, method='POST'):
        """
        请求服务器数据
        :return:
        """
        try:
            if not body:
                body = {}
            url = 'https://lop-proxy.jd.com/' + path
            if method == 'POST':
                response = await session.post(url, json=body)
            else:
                response = await session.get(url, json=body)

            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            self.print('请求服务器数据失败, {}'.format(e.args))
            return {
                'success': False
            }

    async def do_tasks(self, session, times=3):
        """
        做任务
        :return:
        """
        if times < 0:
            return

        flag = False

        res = await self.request(session, '/WonderfulLuckDrawApi/queryMissionList', [{
            "userNo": "$cooMrdGatewayUid$",
            "activityCode": self.activityCode
        }])
        if not res.get('success'):
            self.print('获取任务列表失败!')
            return
        task_list = res['content']['missionList']

        for task in task_list:
            if task['status'] == 10:
                self.print('今日完成任务:{}!'.format(task['title']))
                continue
            flag = True
            if task['status'] == 11:
                for no in task['getRewardNos']:
                    body = [{
                        "activityCode": self.activityCode,
                        "userNo": "$cooMrdGatewayUid$",
                        "getCode": no
                    }]
                    res = await self.request(session, '/WonderfulLuckDrawApi/getDrawChance', body)
                    if res.get('success'):
                        self.print('成功领取一次抽奖机会!')
                        break
                    await asyncio.sleep(2)
                continue

            for i in range(task['completeNum'], task['totalNum']+1):
                body = {
                    "activityCode": self.activityCode,
                    "userNo": "$cooMrdGatewayUid$",
                    "missionNo": task['missionNo'],
                }
                if 'params' in task:
                    body['params'] = task['params']
                res = await self.request(session, '/WonderfulLuckDrawApi/completeMission', [body])
                if res.get('success'):
                    self.print('完成任务:{}-{}'.format(task['title'], i + 1))
                await asyncio.sleep(2.5)

        if flag:
            await self.do_tasks(session)

    async def lottery(self, session):
        """
        抽奖
        :return:
        """
        while True:
            res = await self.request(session, '/WonderfulLuckDrawApi/draw', [{
                "userNo": "$cooMrdGatewayUid$",
                "activityCode": self.activityCode
            }])
            if res.get('success'):
                self.print('抽奖成功')
            else:
                break
            await asyncio.sleep(2)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_tasks(session)
            await self.lottery(session)  # 抽奖


if __name__ == '__main__':
    run_jd(JdDovePolite)
