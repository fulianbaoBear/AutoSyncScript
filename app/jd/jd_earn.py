#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts_v2
# @File    : jd_earn.py
# @Time    : 2022/6/15 10:47 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 32 11 * * *
# @Desc    : 京东赚赚
import asyncio
import json
from datetime import datetime
from urllib.parse import quote

import aiohttp

from app.jd import JdApp, run_jd


class JdEarn(JdApp):

    @property
    def app_name(self):
        """
        :return:
        """
        return "京东赚赚"

    # skey: zwEE6C29D569D7E6A8884CA7545C8F84CACBE62CB573BFCD7DC78B4F0551C47B333DBEDB5ACBE3724D3C46EB25682136ACBED5B9CF4DB7A12CCE787A01B5CD9C9A5C6CC654B46F06212A7EAA57CCDA5E0D83A3F7070789BDBDF8F7FAB000B35842
    # wq_auth_token

    def __init__(self, **kwargs):
        super(JdEarn, self).__init__(**kwargs)
        self.headers.update({
            'content-type': 'application/json',
            'x-requested-with': 'com.jingdong.app.mall',
            'sec-fetch-mode': 'cors',
            'origin': 'https://carry.m.jd.com',
            'sec-fetch-site': 'same-site',
            'wqreferer': 'http://wq.jd.com/wxapp/pages/hd-interaction/task/index',
            'referer': 'https://servicewechat.com/wx8830763b00c18ac3/115/page-frame.html',
        })

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        try:
            if not body:
                body = dict()
            body["mpVersion"] = "3.4.0"
            url = "https://api.m.jd.com/client.action"
            params = {
                'functionId': function_id,
                'body': json.dumps(body),
                'appid': 'wh5',
                'loginType': '1',
                'loginWQBiz': 'interact',
                'g_ty': 'ls',
                'g_tk': '312965635',
            }
            response = await session.get(url, params=params)
            data = await response.json()
            return data
        except Exception as e:
            self.print(f"请求数据失败:{e.args}")
            return {
                'code': -1,
                'data': {},
                'msg': 'error'
            }

    async def do_tasks(self, session):
        """
        :param session:
        :return:
        """
        res = await self.request(session, 'interactTaskIndex')
        if res.get('code', -1) != '0':
            self.print(f"获取任务列表失败, {res}")
            return
        task_list = res['data']['taskDetailResList']

        for item in task_list:

            status = item['status']
            task_name = item['taskName']

            if status == 2:
                self.print(f'任务:《{task_name}》已完成...')
                continue

            body = {
                'taskId': item['taskId'],
                'taskItem': item,
                'actionType': 0,
                'taskToken': item['taskToken']
            }
            res = await self.request(session, 'doInteractTask', body)

            self.print(f"任务:《{task_name}》执行结果:{res}")

    async def run(self):
        """
        :return:
        """
        if not self.wq_auth_token:
            self.print("未配置wq_auth_token, 无法执行...")
            return
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_tasks(session)


if __name__ == '__main__':
    run_jd(JdEarn)
