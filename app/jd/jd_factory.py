#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_factory.py
# @Time    : 2022/4/18 12:04 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 35 6,12,18 * * *
# @Desc    : 东东工厂
import asyncio
import json
from urllib.parse import quote

import aiohttp

from app.jd import JdApp, run_jd


class JdFactory(JdApp):

    def __init__(self, **kwargs):
        super(JdFactory, self).__init__(**kwargs)
        self.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://h5.m.jd.com',
        })
        self.host = 'https://api.m.jd.com/client.action/'

    @property
    def app_name(self):
        return "东东工厂"

    async def request(self, session, function_id=None, params=None, method='post'):
        """
        :param params:
        :param function_id:
        :param session:
        :param method:
        :return:
        """
        if params is None:
            params = {}
        try:
            session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
            url = self.host + '?functionId={}&body={}&client=wh5&clientVersion=1.0.0'.format(function_id,
                                                                                             quote(json.dumps(params)))
            if method == 'post':
                response = await session.post(url=url)
            else:
                response = await session.get(url=url)

            text = await response.text()

            data = json.loads(text)

            if data['code'] != 0:

                return None
            else:
                return data['data']

        except Exception as e:
            self.print('请求服务器数据失败, {}'.format(e.args))
            return None

    async def choose_product(self, session):
        """
        选择商品
        :param session:
        :return:
        """
        data = await self.request(session, 'jdfactory_getProductList', {})
        if not data or data['bizCode'] != 0:
            self.print('{}, 无法获取商品列表!')
            return
        goods_list = sorted(data['result']['canMakeList'], key=lambda i: i.get('sellOut', 0), reverse=False)
        goods_list = sorted(data['result']['canMakeList'], key=lambda i: i.get('couponCount', 0), reverse=True)
        message = '  商品名称\t\t\t商品状态\t\t商品数量\n'

        for goods in goods_list:
            message += '{}\t\t{}\t\t{}\n'.format(goods['name'], '可选' if goods['sellOut'] == 0 else '已抢光',
                                                 goods['couponCount'])

        for goods in goods_list:
            if goods['couponCount'] > 0 and goods['sellOut'] == 0:
                res = await self.request(session, 'jdfactory_makeProduct', {
                    'skuId': goods['skuId']
                })
                if res['bizCode'] == 0:
                    self.print('成功选择商品:《{}》!'.format(goods['name']))
                else:
                    self.print('选择商品《{}》失败, {}!'.format(goods['name'], res['bizMsg']))
                break

    async def init(self, session):
        """
        获取首页数据
        :param session:
        :return:
        """
        self.print('正在初始化数据...')
        data = await self.request(session, 'jdfactory_getHomeData')

        if not data or data['bizCode'] != 0:
            self.print('无法获取活动数据!')
            return False

        data = data['result']

        have_product = data['haveProduct']  # 是否有生产的商品

        if have_product == 2:  # 未选择商品
            self.print('此账号未选择商品, 现在为您从库存种选择商品!\n')
            await self.choose_product(session)

        self.print('初始化数据完成!')
        return True

    async def collect_electricity(self, session):
        """
        收集电量
        :param session:
        :return:
        """
        data = await self.request(session, 'jdfactory_collectElectricity')

        if not data or data['bizCode'] != 0:
            self.print('收集电量失败!')
        else:
            self.print('成功收集{}电量, 当前蓄电池总电量{}!'.
                       format(data['result']['electricityValue'], data['result']['batteryValue']))

    async def get_task_list(self, session):
        """
        获取任务列表
        :param session:
        :return:
        """
        data = await self.request(session, 'jdfactory_getTaskDetail')

        if not data or data['bizCode'] != 0:
            self.print('无法获取任务列表!')
            return

        task_list = data['result']['taskVos']

        for task in task_list:
            if task['taskType'] == 14:  # 互助码
                task_list.remove(task)
                break

        return task_list

    async def daily_clock_in(self, session, task):
        """
        每日打卡
        :param session:
        :param task:
        :return:
        """
        self.print('正在进行任务:{}!'.format(task['taskName']))

        data = await self.request(session, 'jdfactory_collectScore', {
            'taskToken': task['simpleRecordInfoVo']['taskToken']
        })

        if not data or data['bizCode'] != 0:
            self.print('无法完成任务:{}, {}'.format(task['taskName'], data['bizMsg']))
        else:
            self.print('完成任务:{}, {}'.format(task['taskName'], data['bizMsg']))

    async def daily_patrol_factory(self, session, task):
        """
        每日巡厂
        :param task:
        :param session:
        :return:
        """
        self.print('正在进行任务:{}!'.format(task['taskName']))

        if task['threeMealInfoVos'][0]['status'] == 0:
            self.print('任务:{}已错过时间!'.format(task['taskName']))
            return

        data = await self.request(session, 'jdfactory_collectScore', {
            'taskToken': task['threeMealInfoVos'][0]['taskToken']
        })

        if data['bizCode'] != 0:
            self.print('无法完成任务:{}!'.format(task['taskName']))
        else:
            self.print('完成任务:{}, 获得:{}电量!'.format(task['taskName'], data['result']['score']))

    async def click_jd_electric(self, session, task):
        """
        京东首页点击京东电器
        :param session:
        :param task:
        :return:
        """
        self.print('{}, 正在进行任务:{}!'.format(self.account, task['taskName']))
        try:
            url = 'https://api.m.jd.com/?client=wh5&clientVersion=1.0.0&functionId=queryVkComponent&body=%7B' \
                  '%22businessId%22%3A%22babel%22%2C%22componentId%22%3A%224f953e59a3af4b63b4d7c24f172db3c3%22%2C' \
                  '%22taskParam%22%3A%22%7B%2522actId%2522%3A%25228tHNdJLcqwqhkLNA8hqwNRaNu5f%2522%7D%22%7D' \
                  '&_timestamp=1625621328362'
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != '0':
                self.print('无法完成任务:{}!'.format(task['taskName']))
                return
        except Exception as e:
            self.print('无法完成任务:{}, {}!'.format(task['taskName'], e.args))
            return

        await asyncio.sleep(1)

        data = await self.request(session, 'jdfactory_collectScore',
                                  {'taskToken': task['simpleRecordInfoVo']['taskToken']})

        if data['bizCode'] != 0:
            self.print('无法完成任务:{}!'.format(task['taskName']))
        else:
            self.print('完成任务:{}, 获得电量:{}!'.format(task['taskName'], data['result']['score']))

    async def visit_meeting_place(self, session, task):
        """
        逛会场
        :param session:
        :param task:
        :return:
        """
        self.print('正在进行任务:{}!'.format(task['taskName']))

        for item in task['shoppingActivityVos']:
            if item['status'] == 1:
                data = await self.request(session, 'jdfactory_collectScore', {
                    'taskToken': item['taskToken']
                })
                if data['bizCode'] == 0:
                    self.print('任务:{}执行成功, 获得电量:{}, 任务进度:{}/{}'.
                               format(task['taskName'], data['result']['score'],
                                      data['result']['times'], data['result']['maxTimes']))
                else:
                    self.print('完成任务:{}失败!'.format(task['taskName']))

    async def follow_shop(self, session, task):
        """
        关注店铺任务
        :param session:
        :param task:
        :return:
        """
        for item in task['followShopVo']:
            res = await self.request(session, 'jdfactory_collectScore', {
                'taskToken': item['taskToken']
            })
            if not res or res['bizCode'] != 0:
                self.print('无法完成任务:{}!'.format(item))
            else:
                self.print('任务:{}执行成功, 获得电量:{}, 任务进度:{}/{}'.
                           format(task['taskName'], res['result']['score'],
                                  res['result']['times'], res['result']['maxTimes']))

    async def view_event_calendar(self, session, task):
        """
        活动日历
        :param task:
        :param session:
        :return:
        """
        for item in task['shoppingActivityVos']:

            if item['status'] == 2:
                self.print('任务已完成:{}!'.format(item['title']))
                continue
            res = await self.request(session, 'jdfactory_collectScore', {
                'taskToken': item['taskToken'],
                'actionType': '1'
            })
            if not res or res['bizCode'] != 0:
                self.print('无法进行任务:{}!'.format(item['title']))
                continue
            if 'waitDuration' in item:
                wait = item['waitDuration']
            else:
                wait = 5
            self.print('正在进行任务:{}, 需要等待{}秒!'.format(item['title'], wait))
            await asyncio.sleep(wait)

            res = await self.request(session, 'jdfactory_collectScore', {
                'taskToken': item['taskToken'],
                'actionType': '2'
            })
            if not res or res['bizCode'] != 0:
                self.print('无法完成任务:{}!'.format(item['title']))
                continue

            self.print('任务:{}执行成功, 获得电量:{}, 任务进度:{}/{}'.format(item['title'],
                                                               res['result']['score'], res['result']['times'],
                                                               res['result']['maxTimes']))

    async def purchase_of_goods(self, session, task):
        """
        商品加购任务
        :param session:
        :param task:
        :return:
        """
        self.print('{}, 正在进行任务:{}!'.format(self.account, task['taskName']))

        for i in range(len(task['productInfoVos'])):
            item = task['productInfoVos'][i]
            self.print('正在进行第{}次任务:{}!'.format(i + 1, task['taskName']))
            res = await self.request(session, 'jdfactory_collectScore', {
                'taskToken': item['taskToken']})
            if not res or res['bizCode'] != 0:
                self.print('无法完成第{}次任务:{}!'.format(i + 1, task['taskName']))
            else:
                self.print('完成第{}次任务:{}, 获得电量:{}, 任务进度:{}/{}'.
                           format(i + 1, task['taskName'], res['result']['score'],
                                  res['result']['times'], res['result']['maxTimes']))

                if res['result']['times'] >= res['result']['maxTimes']:
                    break

    async def do_tasks(self, session, task_list):
        """
        做任务
        :param session:
        :param task_list:
        :return:
        """
        for task in task_list:
            if task['status'] != 1:
                self.print('任务:{}已做完!'.format(task['taskName']))
                continue

            if task['taskType'] == 13:  # 每日打卡
                await self.daily_clock_in(session, task)

            elif task['taskType'] == 14:  # 助力好友
                self.print('任务:{}, 进度{}/{}!'.format(task['taskName'], task['times'], task['maxTimes']))

            elif task['taskType'] == 10:  # 每日巡厂
                await self.daily_patrol_factory(session, task)

            elif task['taskType'] == 21:  # 入会任务
                self.print('跳过入会任务:{}!'.format(task['taskName']))

            elif task['taskType'] == 23:  # 京东首页点击京东电器
                await self.click_jd_electric(session, task)

            elif task['taskType'] == 3:  # 逛会场
                await self.visit_meeting_place(session, task)

            elif task['taskType'] == 1:  # 关注店铺任务
                await self.follow_shop(session, task)

            elif task['taskType'] == 9:  # 活动日历
                await self.view_event_calendar(session, task)

            elif task['taskType'] == 15:  # 浏览加购
                await self.purchase_of_goods(session, task)

            elif task['taskType'] == 19:  # 跳过下单任务
                self.print('跳过任务:{}!'.format(task['taskName']))

            else:
                self.print('任务:{}功能未实现!'.format(task['taskName']))

    async def insert_electricity(self, session):
        """
        电量超过300万则加电一次, 满足兑换商品时全投
        :return:
        """
        data = await self.request(session, 'jdfactory_getHomeData')
        if not data or data['bizCode'] != 0:
            self.print('无法获取电量数据!')
            return

        # 当前存储的电量
        cur_electricity = data['result']['factoryInfo']['remainScore']
        total_electricity = data['result']['factoryInfo']['totalScore']  # 兑换商品总共需要电量
        used_electricity = data['result']['factoryInfo']['useScore']  # 当前投入电量

        if int(cur_electricity) >= 300 * 10000:  # 电量已存满，加电一次
            data = await self.request(session, 'jdfactory_addEnergy')
            if data or data['bizCode'] != 0:
                self.print('加电失败!')
            else:
                self.print('成功加电1次!')

        # 电量足够换到商品, 全加
        if int(cur_electricity) + int(used_electricity) >= int(total_electricity):
            while True:
                data = await self.request(session, 'jdfactory_addEnergy')
                if data or data['bizCode'] != 0:
                    self.print('加电失败!')
                    break
                else:
                    self.print('成功加电1次!')
                await asyncio.sleep(2)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            is_success = await self.init(session)
            if not is_success:
                self.print('{}, 无法初始化数据, 退出程序!')
                return

            await self.collect_electricity(session)
            task_list = await self.get_task_list(session)
            await self.do_tasks(session, task_list)
            await self.insert_electricity(session)


if __name__ == '__main__':
    run_jd(JdFactory)
