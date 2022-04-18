#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_speed_sign.py
# @Time    : 2022/4/19 3:21 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 10 7 * * *
# @Desc    : 京东极速版app 签到和金币任务
import asyncio
import hmac
import json
import time
from urllib.parse import quote, urlencode

import aiohttp

from app.jd import JdApp, run_jd


class JdSpeedSign(JdApp):

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super(JdSpeedSign, self).__init__(**kwargs)
        self.canStartNewItem = None
        self.task_name = None
        self.headers.update({
            'Host': 'api.m.jd.com',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'user-agent': 'jdltapp;iPad;3.1.0;14.4;network/wifi;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1")',
            'Accept-Language': 'zh-Hans-CN;q=1,en-CN;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': "application/x-www-form-urlencoded",
            "referer": "https://an.jd.com/babelDiy/Zeus/q1eB6WUB8oC4eH1BsCLWvQakVsX/index.html"
        })
        self.score = 0  # 本次获得金币
        self.total = 0  # 总金币
        self.host = 'https://api.m.jd.com/'

    @property
    def app_name(self):
        """
        :return:
        """
        return "京东极速版签到/赚金币"

    async def request_sign(self, session, function_id, body=None, method='GET'):
        """
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        headers = {
            'Host': 'api.m.jd.com',
            'accept': '*/*',
            'kernelplatform': 'RN',
            'user-agent': 'JDMobileLite/3.1.0 (iPad; iOS 14.4; Scale/2.00)',
            'accept-language': 'zh-Hans-CN;q=1, ja-CN;q=0.9'
        }
        timestamp = int(time.time() * 1000)
        if not body:
            body = {}
        body_str = json.dumps(body)
        content = f'lite-android&{body_str}&android&3.1.0&{function_id}&{timestamp}&846c4c32dae910ef'
        key = '12aea658f76e453faf803d15c40a72e0'
        sign = hmac.new(key.encode('utf-8'), content.encode('utf-8'), 'SHA256').hexdigest()
        url = f'https://api.m.jd.com/api?functionId={function_id}&body={quote(body_str)}&appid=lite-android&client=android&uuid=846c4c32dae910ef&clientVersion=3.1.0&t={timestamp}&sign={sign}'

        try:
            response = await session.get(url, headers=headers)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            self.print('请求服务器数据失败,{}!'.format(e.args))

    async def request(self, session, function_id, body=None, method='GET'):
        """
        无sign请求
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        timestamp = int(time.time() * 1000)
        default_params = {
            'functionId': function_id,
            'appid': 'activities_platform',
            '_t': timestamp
        }
        if not body:
            body = {}
        default_params['body'] = json.dumps(body)
        try:
            if method == 'GET':
                url = self.host + '?' + urlencode(default_params)
                response = await session.get(url, headers=self.headers)
            elif method == 'POST':
                url = self.host
                response = await session.post(url, data=urlencode(default_params), headers=self.headers)
            text = await response.text()
            data = json.loads(text)
            if data['code'] == 0:
                return data['data']
            else:
                self.print('请求服务器数据失败({})!'.format(data))
                return data
        except Exception as e:
            self.print('请求服务器数据失败,{}!'.format(e.args))
            return {}

    async def rich_man_index(self, session):
        """
        红包大富翁首页
        :param session:
        :return:
        """
        body = {
            "actId": "hbdfw",
            "needGoldToast": "true"
        }
        data = await self.request_sign(session, 'richManIndex', body)
        try:
            if data['code'] == 0 and data['data']:
                self.print('{}'.format(data['data']))
                randomTimes = data['data']['userInfo']['randomTimes']
                while randomTimes > 0:
                    await self.shoot_rich_man_dice(session)
                    randomTimes -= 1
            else:
                self.print('{}'.format(data.get('msg')))
        except Exception as e:
            self.print('红包大富翁 请求服务器数据失败,{}({})!'.format(e.args, data))

    async def shoot_rich_man_dice(self, session):
        """红包大富翁
        """
        body = {
            "actId": "hbdfw"
        }
        data = await self.request_sign(session, 'shootRichManDice', body)
        try:
            if data['code'] == 0 and not data.get('data') and not data['data'].get('rewardType') and \
                    not data['data'].get('couponDesc'):
                self.print('红包大富翁抽奖获得：【{}-{} {}】'.format(data['data']['couponUsedValue'], data['data']['rewardValue'],
                                                         data['data']['poolName']))
            else:
                self.print('红包大富翁抽奖：获得空气')
        except Exception as e:
            self.print('红包大富翁抽奖 请求服务器数据失败,{}!'.format(e.args))

    async def wheels_home(self, session):
        """
        大转盘
        :param session:
        :return:
        """
        body = {
            "linkId": "toxw9c5sy9xllGBr3QFdYg"
        }
        data = await self.request(session, 'wheelsHome', body)
        try:
            if data['lotteryChances'] > 0:
                times = data['lotteryChances']
                while times > 0:
                    await self.wheels_lottery(session)
                    times -= 1
                    await asyncio.sleep(0.5)
            else:
                self.print('大转盘 已无次数!')
        except Exception as e:
            self.print('大转盘 请求服务器数据失败,{}!'.format(e.args))

    async def wheels_lottery(self, session):
        """
        大转盘抽奖
        :param session:
        :return:
        """
        body = {
            "linkId": "toxw9c5sy9xllGBr3QFdYg"
        }
        data = await self.request(session, 'wheelsLottery', body)
        try:
            if data['rewardType']:
                # prizeCode
                desc = data.get('couponDesc')
                if not desc:
                    desc = data.get('prizeCode')
                self.print('幸运大转盘抽奖获得:【{}-{} {}】'.format(data.get('couponUsedValue'), data.get('rewardValue'), desc))
        except Exception as e:
            self.print('大转盘抽奖 请求服务器数据失败,{}({})!'.format(e.args, data))

    async def ap_task_list(self, session):
        """
        获取大转盘任务列表
        :param session:
        :return:
        """
        body = {
            "linkId": "toxw9c5sy9xllGBr3QFdYg"
        }
        self.print('开始做大转盘任务...')
        data = await self.request(session, 'apTaskList', body)
        try:
            for task in data:
                if task['taskFinished'] == False and task['taskType'] in ['SIGN', 'BROWSE_CHANNEL']:
                    self.print('去做任务: {}'.format(task['taskTitle']))
                    await self.ap_do_task(session, task['taskType'], task['id'], 4, task['taskSourceUrl'])
                else:
                    self.print('任务 {} 已做过, 跳过.'.format(task['taskTitle']))
        except Exception as e:
            self.print('大转盘任务 请求服务器数据失败,{}({})!'.format(e.args, data))

    async def ap_do_task(self, session, task_type, task_id, channel, item_id):
        """
        大转盘做任务
        :param session:
        :param task_type:
        :param task_id:
        :param channel:
        :param item_id:
        :return:
        """
        body = {
            "linkId": "toxw9c5sy9xllGBr3QFdYg",
            "taskType": task_type,
            "taskId": task_id,
            "channel": channel,
            "itemId": item_id
        }
        data = await self.request(session, 'apDoTask', body)
        try:
            if data['finished']:
                self.print('任务完成!')
        except Exception as e:
            self.print('大转盘做任务失败,{}({})!'.format(e.args, data))

    async def sign_init(self, session):
        """
        签到 init
        :param session:
        :return:
        """
        body = {
            "activityId": "8a8fabf3cccb417f8e691b6774938bc2",
            "kernelPlatform": "RN",
            "inviterId": "U44jAghdpW58FKgfqPdotA=="
        }
        data = await self.request_sign(session, 'speedSignInit', body)
        try:
            self.print('sign_init {}'.format(data))
        except Exception as e:
            self.print('签到 请求服务器数据失败,{}({})!'.format(e.args, data))

    async def sign(self, session):
        """
        签到
        :param session:
        :return:
        """
        body = {
            "kernelPlatform": "RN",
            "activityId": "8a8fabf3cccb417f8e691b6774938bc2",
            "noWaitPrize": "false"
        }
        data = await self.request_sign(session, 'speedSign', body)
        try:
            if data['subCode'] == 0:
                self.print('签到得到{}现金,共计获得{}'.format(data['data']['signAmount'],
                                                    data['data']['cashDrawAmount']))
            else:
                self.print('签到失败!({})'.format(data))
        except Exception as e:
            self.print('签到 请求服务器数据失败,{}({})!'.format(e.args, data))

    async def task_list(self, session):
        """
        金币任务列表
        :param session:
        :return:
        """
        body = {
            "version": "3.1.0",
            "method": "newTaskCenterPage",
            "data": {
                "channel": 1
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            for task in data['data']:
                self.task_name = task['taskInfo']['mainTitle']
                if task['taskInfo']['status'] == 0:
                    if task['taskType'] >= 1000:
                        await self.do_task(session, task['taskType'])
                        await asyncio.sleep(1)
                    else:
                        self.canStartNewItem = True
                        while self.canStartNewItem:
                            if task['taskType'] != 3:
                                await self.query_item(session, task['taskType'])
                            else:
                                await self.start_item(session, "", task['taskType'])
                else:
                    self.print('{} 已做过, 跳过.'.format(self.task_name))
        except Exception as e:
            self.print('大转盘任务 请求服务器数据失败,{}({})!'.format(e.args, data))

    async def do_task(self, session, task_id):
        """
        做金币任务
        :param session:
        :param task_id:
        :return:
        """
        body = {
            "method": "marketTaskRewardPayment",
            "data": {
                "channel": 1,
                "clientTime": int(time.time() * 1000) + 0.588,
                "activeType": task_id
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if data['code'] == 0:
                self.print('{} 任务已完成,预计获得{}金币'.format(data['data']['taskInfo']['mainTitle'],
                                                      data['data']['reward']))
        except Exception as e:
            self.print('做任务失败,{}({})!'.format(e.args, data))

    async def query_item(self, session, active_type):
        """
        查询商品任务
        :param session:
        :param active_type:
        :return:
        """
        body = {
            "method": "queryNextTask",
            "data": {
                "channel": 1,
                "activeType": active_type
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if data['code'] == 0:
                await self.start_item(session, data['data']['nextResource'], active_type)
            else:
                self.print('商品任务开启失败,{}!'.format(data['message']))
                self.canStartNewItem = False
        except Exception as e:
            self.print('商品任务开启失败.{}({})!'.format(e.args, data))
            self.canStartNewItem = False

    async def start_item(self, session, active_id, active_type):
        """
        开启商品任务
        :param session:
        :param active_id:
        :param active_type:
        :return:
        """
        body = {
            "method": "enterAndLeave",
            "data": {
                "activeId": active_id,
                "clientTime": int(time.time() * 1000),
                "channel": "1",
                "messageType": "1",
                "activeType": active_type,
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if data['code'] == 0:
                if data['data']['taskInfo']['isTaskLimit'] == 0:
                    video_browsing = data['data']['taskInfo'].get('videoBrowsing')
                    task_completion_progress = data['data']['taskInfo']['taskCompletionProgress']
                    task_completion_limit = data['data']['taskInfo']['taskCompletionLimit']
                    if active_type != 3:
                        video_browsing = 5 if active_type == 1 else 10
                    self.print(
                        f'【{task_completion_progress + 1}/{task_completion_limit}】浏览商品任务记录成功，等待{video_browsing}秒')
                    await asyncio.sleep(video_browsing)
                    await self.end_item(session, data['data']['uuid'], active_type, active_id,
                                        video_browsing if active_type == 3 else "")
                else:
                    self.print('{}任务已达上限!'.format(self.task_name))
                    self.canStartNewItem = False
            else:
                self.print('商品任务开启失败,{}!'.format(data['message']))
                self.canStartNewItem = False
        except Exception as e:
            self.print('商品任务开启失败.{}({})!'.format(e.args, data))
            self.canStartNewItem = False

    async def end_item(self, session, uuid, active_type, active_id="", video_time_length=""):
        """
        结束商品任务
        :param session:
        :param uuid:
        :param active_type:
        :param active_id:
        :param video_time_length:
        :return:
        """
        body = {
            "method": "enterAndLeave",
            "data": {
                "channel": "1",
                "clientTime": int(time.time() * 1000),
                "uuid": uuid,
                "videoTimeLength": video_time_length,
                "messageType": "2",
                "activeType": active_type,
                "activeId": active_id
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if data['code'] == 0 and data['isSuccess']:
                await self.reward_item(session, uuid, active_type, active_id, video_time_length)
            else:
                self.print('{}任务结束失败{}!'.format(self.task_name, data['message']))
        except Exception as e:
            self.print('任务结束失败{}({})!'.format(e.args, data))

    async def reward_item(self, session, uuid, active_type, active_id="", video_time_length=""):
        """
        领取商品任务奖励金币
        :param session:
        :param uuid:
        :param active_type:
        :param active_id:
        :param video_time_length:
        :return:
        """
        body = {
            "method": "rewardPayment",
            "data": {
                "channel": "1",
                "clientTime": int(time.time() * 1000),
                "uuid": uuid,
                "videoTimeLength": video_time_length,
                "messageType": "2",
                "activeType": active_type,
                "activeId": active_id
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if data['code'] == 0 and data['isSuccess']:
                self.score += data['data']['reward']
                self.print('{}任务完成,获得{}金币!'.format(self.task_name, data['data']['reward']))
            else:
                self.print('{}任务失败{}!'.format(self.task_name, data['message']))
        except Exception as e:
            self.print('任务失败{}({})!'.format(e.args, data))

    async def query_joy(self, session):
        """
        查询气泡
        :param session:
        :return:
        """
        body = {
            "method": "queryJoyPage",
            "data": {
                "channel": 1
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if 'taskBubbles' in data['data']:
                for task in data['data']['taskBubbles']:
                    await self.reward_task(session, task['id'], task['activeType'])
                    await asyncio.sleep(0.5)
        except Exception as e:
            self.print('收气泡失败{}!'.format(e.args))

    async def reward_task(self, session, _id, task_id):
        """
        领取气泡奖励
        :param session:
        :param _id:
        :param task_id:
        :return:
        """
        body = {
            "method": "joyTaskReward",
            "data": {
                "id": _id,
                "channel": 1,
                "clientTime": int(time.time() * 1000) + 0.588,
                "activeType": task_id
            }
        }
        data = await self.request_sign(session, 'ClientHandleService.execute', body)
        try:
            if data['code'] == 0:
                self.score += data['data']['reward']
                self.print('气泡收取成功，获得{}金币!'.format(data['data']['reward']))
            else:
                self.print('气泡收取失败，{}!'.format(data['message']))
        except Exception as e:
            self.print('气泡收取失败，{}({})!'.format(e.args, data))

    async def cash(self, session):
        """
        获取当前金币
        :param session:
        :return:
        """
        body = {
            "method": "userCashRecord",
            "data": {
                "channel": 1,
                "pageNum": 1,
                "pageSize": 20
            }
        }
        data = await self.request_sign(session, 'MyAssetsService.execute', body)
        try:
            if data['code'] == 0:
                self.total = data['data']['goldBalance']
        except Exception as e:
            self.print('获取cash信息失败，{}({})!'.format(e.args, data))

    async def show_msg(self):
        """
        show msg
        :return:
        """
        self._result_msg = f'【京东账号】{self.account}\n'
        gold_tips = f'【运行结果】本次运行获得{self.score}金币，共计{self.total}金币'
        self._result_msg += f'{gold_tips}\n'
        self._result_msg += f'【红包】可兑换 {self.total / 10000:.2f} 元京东红包\n'
        self._result_msg += f'【兑换入口】京东极速版->我的->金币\n'
        self.print(self._result_msg)

    async def run(self):
        """run
        """
        async with aiohttp.ClientSession(cookies=self.cookies) as session:
            # 暂时过期
            # await self.rich_man_index(session)

            await self.wheels_home(session)
            await self.ap_task_list(session)
            await self.wheels_home(session)

            # await self.sign_init(session)
            # await self.sign(session)

            await self.task_list(session)
            await self.query_joy(session)
            # await self.sign_init(session)
            await self.cash(session)
            await self.show_msg()


if __name__ == '__main__':
    run_jd(JdSpeedSign)
