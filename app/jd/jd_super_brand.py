#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_super_brand.py
# @Time    : 2022/4/18 2:35 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 30 10,14,20 * * *
# @Desc    : 特物Z
import asyncio
import json
import time
from urllib.parse import urlencode

import aiohttp

from app.jd import JdApp, run_jd


class JdSuperBrand(JdApp):

    def __init__(self, **kwargs):
        super(JdSuperBrand, self).__init__(**kwargs)
        self.headers.update({
            'referer': 'https://pro.m.jd.com/mall/active/4NwAuHsFZZfedc7NJGoVMvK2WkKD/index.html',
            'origin': 'https://pro.m.jd.com',
        })
        self.encrypt_project_id = None
        self.activity_id = None

    @property
    def app_name(self):
        return "特物Z"

    async def request(self, session, function_id, body=None, method='POST'):
        """
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
                'appid': 'ProductZ4Brand',
                'client': 'wh5',
                't': int(time.time() * 1000),
                'body': json.dumps(body)
            }
            url = 'https://api.m.jd.com/api?' + urlencode(params)

            if method == 'POST':
                response = await session.post(url)
            else:
                response = await session.get(url)

            text = await response.text()

            data = json.loads(text)

            if data.get('code') != '0':
                return data
            else:
                data = data['data']
                data['code'] = data.pop('bizCode')
                try:
                    data['code'] = int(data['code'])
                except:
                    pass
                data['msg'] = data.pop('bizMsg')

                return data

        except Exception as e:
            self.print('请求数据失败, {}!'.format(e.args))
            return {
                'code': 999,
                'msg': '请求数据失败'
            }

    async def init(self, session):
        """
        获取首页数据
        :return:
        """
        data = await self.request(session, 'superBrandSecondFloorMainPage', {"source": "secondfloor"})
        if data.get('code') != 0:
            return False
        self.encrypt_project_id = data['result']['activityBaseInfo']['encryptProjectId']
        self.activity_id = data['result']['activityBaseInfo']['activityId']
        return True

    async def do_tasks(self, session):
        """
        获取任务列表
        :param session:
        :return:
        """
        data = await self.request(session, 'superBrandTaskList', {
            "source": "secondfloor",
            "activityId": self.activity_id,
            "assistInfoFlag": 1})
        if data.get('code') != 0:
            self.print('获取任务列表数据失败!')
            return None

        task_list = data['result']['taskList']

        for task in task_list:

            if '助力' in task['assignmentName'] or '邀请' in task['assignmentName']:
                continue

            if not task['ext']:
                item_id = 'null'
            else:
                if 'followShop' in task['ext']:
                    item_id = task['ext']['followShop'][0]['itemId']
                elif 'assistTaskDetail' in task['ext']:
                    item_id = task['ext']['assistTaskDetail']['itemId']
                elif 'brandMemberList' in task['ext']:
                    item_id = task['ext']['brandMemberList'][0]['itemId']
                elif 'sign2' in task['ext']:
                    item_id = task['ext']['currentSectionItemId']
                else:
                    item_id = 'null'

            body = {
                "source": "secondfloor",
                "activityId": self.activity_id,
                "encryptProjectId": self.encrypt_project_id,
                "encryptAssignmentId": task['encryptAssignmentId'],
                "assignmentType": task['assignmentType'],
                "completionFlag": 1,
                "itemId": item_id,
                "actionType": 0}
            res = await self.request(session, 'superBrandDoTask', body)
            self.print('任务:{}, {}'.format(task['assignmentName'], res.get('msg')))
            await asyncio.sleep(1)

    async def lottery(self, session):
        """
        抽奖
        :return:
        """
        while True:
            res = await self.request(session, 'superBrandTaskLottery', {
                "source": "secondfloor",
                "activityId": self.activity_id})
            if res.get('code') == "TK000":
                award = res['result']['userAwardInfo']
                if not award:
                    award = '无'
                elif award.get('awardType') == 3:
                    award = '{}京豆'.format(award['beanNum'])
                self.print('抽奖成功, 获得:{}'.format(award))
            else:
                break
            await asyncio.sleep(1)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            if not await self.init(session):
                self.print('初始化失败, 退出程序!')
                return
            await self.do_tasks(session)
            await self.lottery(session)


if __name__ == '__main__':
    run_jd(JdSuperBrand)
