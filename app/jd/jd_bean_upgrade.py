#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_bean_upgrade.py
# @Time    : 2022/4/18 11:41 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 5 1 * * *
# @Desc    : 升级赚京豆
import asyncio
import json
from urllib.parse import quote

import aiohttp

from app.jd import JdApp, run_jd
from com.functions import random_string


class JdBeanUpgrade(JdApp):
    
    def __init__(self, **kwargs):
        super(JdBeanUpgrade, self).__init__(**kwargs)
        self.headers.update({
            'Host': 'api.m.jd.com',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Referer': 'https://h5.m.jd.com/rn/42yjy8na6pFsq1cx9MJQ5aTgu3kX/index.html',
        })
        self.id = random_string(40)
    
    @property
    def app_name(self):
        return "升级赚京豆"
    
    async def request(self, session, function_id='', body=None, method='GET'):
        """
        请求数据
        :return:
        """
        try:
            if not body:
                body = {}
            url = 'https://api.m.jd.com/client.action?' \
                  'functionId={}&body={}&appid=ld&client=m&' \
                  'uuid={}&openudid={}'.format(function_id, quote(json.dumps(body)), self.id, self.id)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            self.print('获取数据失败:{}!'.format(e.args))

    async def do_task(self, session):
        """
        做任务
        :param session:
        :return:
        """
        data = await self.request(session, 'beanTaskList', {"viewChannel": "AppHome"})
        if data['code'] != '0':
            self.print('获取任务失败!')
            return
        data = data['data']

        for task in data['taskInfos']:
            task_name = task['taskName']

            if task['status'] == 2:  # 任务已完成
                continue
            if task['taskType'] == 3:
                action_type = 0
            else:
                action_type = 1
            res = await self.request(session, 'beanDoTask', {
                "actionType": action_type,
                "taskToken": task['subTaskVOS'][0]['taskToken']
            })

            if 'errorCode' in res:
                self.print('任务:{}, {}'.format(task_name, res['errorMessage']))
            elif 'data' in res and 'bizMsg' in res['data']:
                self.print('任务:{},  {}'.format(task_name, res['data']['bizMsg']))
            else:
                self.print('任务:{}, {}'.format(task_name, res))

            if task['taskType'] != 3:
                self.print('任务:{}等待5秒...'.format(task_name))
                await asyncio.sleep(5)
                res = await self.request(session, 'beanDoTask',
                                         {"actionType": 0, "taskToken": task['subTaskVOS'][0]['taskToken']})

                if 'data' in res and 'bizMsg' in res['data']:
                    self.print('任务:{},  {}'.format(task_name, res['data']['bizMsg']))
                elif 'errorCode' in res:
                    self.print('任务:{}, {}'.format(task_name, res['errorMessage']))
                else:
                    self.print('任务:{}, {}'.format(task_name, res))

            await asyncio.sleep(3)

    async def run(self):
        """
        入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_task(session)
    

if __name__ == '__main__':
    run_jd(JdBeanUpgrade)
