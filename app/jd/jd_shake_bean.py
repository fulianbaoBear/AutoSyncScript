#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_shake_bean.py
# @Time    : 2022/4/18 2:21 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 3 3 * * *
# @Desc    : 摇京豆
import asyncio
import json
import time
from urllib.parse import urlencode

import aiohttp

from app.jd import JdApp, run_jd


class JdShakeBean(JdApp):

    def __init__(self, **kwargs):
        super(JdShakeBean, self).__init__(**kwargs)
        self.headers.update({
            'origin': 'https://spa.jd.com',
            'referer': 'https://spa.jd.com/home?source=JingDou',
            'accept': 'application/json'
        })
        self.METHOD_GET = 'get'
        self.METHOD_POST = 'post'
        self.nickname = None
        self.sign_info = {}
        self.bean_count = 0
        self.red_packet_num = 0
        self.coupon_list = []

    @property
    def app_name(self):
        return "摇京豆"

    async def request(self, session, params=None, method='get'):
        """
        get 请求
        :param params:
        :param method:
        :param session:
        :return:
        """
        if params is None:
            params = {}

        url = 'https://api.m.jd.com/?{}'.format(urlencode(params))

        try:
            if method == self.METHOD_POST:
                response = await session.post(url)
            else:
                response = await session.get(url)
            text = await response.text()
            data = json.loads(text)
            await asyncio.sleep(1)
            return data
        except Exception as e:
            self.print(f'请求服务器错误, {e.args}')

    async def get_index_data(self, session):
        """
        获取首页数据
        :param session:
        :return:
        """
        params = {
            't': int(time.time() * 1000),
            'functionId': 'pg_channel_page_data',
            'appid': 'sharkBean',
            'body': {"paramData": {"token": "dd2fb032-9fa3-493b-8cd0-0d57cd51812d"}}
        }
        self.print('获取摇京豆首页数据...')
        data = await self.request(session, params, self.METHOD_GET)
        return data

    async def daily_sign(self, session):
        """
        每日签到
        :param session:
        :return:
        """
        data = await self.get_index_data(session)
        if 'data' not in data or 'floorInfoList' not in data['data']:
            self.print('无法获取签到数据:{}'.format(data))
            return

        sign_info = None

        for floor_info in data['data']['floorInfoList']:
            if 'code' in floor_info and floor_info['code'] == 'SIGN_ACT_INFO':
                cursor = floor_info['floorData']['signActInfo']['currSignCursor']
                token = floor_info['token']
                sign_info = {
                    'status': '',
                    'body': {
                        "floorToken": token,
                        "dataSourceCode": "signIn",
                        "argMap": {
                            "currSignCursor": cursor
                        }
                    }
                }
                for item in floor_info['floorData']['signActInfo']['signActCycles']:
                    if item['signCursor'] == cursor:
                        sign_info['status'] = item['signStatus']

        if not sign_info:
            self.print('查找签到数据失败, 无法签到！')
            return

        if sign_info['status'] != -1:
            self.print('当前状态无法签到, 可能已签到过!')
            return

        # 签到参数
        sign_params = {
            't': int(time.time() * 1000),
            'functionId': 'pg_interact_interface_invoke',
            'appid': 'sharkBean',
            'body': sign_info['body'],
        }

        res = await self.request(session, sign_params, self.METHOD_POST)
        if res.get('success', False):
            self.print('签到成功!')
            for reward in res['data']['rewardVos']:
                if reward['jingBeanVo'] is not None:
                    self.bean_count += int(reward['jingBeanVo']['beanNum'])
                if reward['hongBaoVo'] is not None:
                    self.red_packet_num = float(self.red_packet_num) + float(reward['hongBaoVo'])
        else:
            self.print('签到失败!')

    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        self.print('开始做浏览任务！')
        params = {
            't': int(time.time()),
            'appid': 'vip_h5',
            'functionId': 'vvipclub_lotteryTask',
            'body': {"info": "browseTask", "withItem": 'true'}
        }
        data = await self.request(session, params, self.METHOD_GET)
        if 'data' not in data:
            self.print('获取任务列表失败, 无法做任务!')
            return

        for item in data['data']:
            if 'taskItems' not in item:
                continue
            for task in item['taskItems']:
                if task['finish']:
                    self.print('任务: {}, 今日已完成!'.format(task['title']))
                    continue
                params = {
                    'appid': 'vip_h5',
                    'functionId': 'vvipclub_doTask',
                    'body': {
                        "taskName": "browseTask",
                        "taskItemId": task['id']
                    }
                }
                res = await self.request(session, params, self.METHOD_GET)
                if res.get('success', False):
                    self.print('完成{}任务!'.format(task['title']))
                else:
                    self.print('{}{}任务失败, {}!'.format(task['title'], task['subTitle'], res))

                await asyncio.sleep(1.5)

        self.print('完成浏览任务！')

    async def get_shake_times(self, session):
        """
        获取当前摇奖次数
        :return:
        """
        data = await self.get_index_data(session)
        shake_times = 0
        if 'data' not in data or 'floorInfoList' not in data['data']:
            self.print('无法获取摇盒子次数!')
            return shake_times
        for floor in data['data']['floorInfoList']:
            if 'code' in floor and floor['code'] == 'SHAKING_BOX_INFO':
                shake_times = floor['floorData']['shakingBoxInfo']['remainLotteryTimes']
        return shake_times

    async def do_shake(self, session, times=0):
        """
        摇盒子
        :param session:
        :param times:
        :return:
        """
        if times == 0:
            self.print('当前无摇盒次数！')
        else:
            self.print('总共可以摇{}次!'.format(times))
        for i in range(times):
            self.print('进行第{}次摇奖!'.format(i + 1))
            params = {
                'appid': 'sharkBean',
                'functionId': 'vvipclub_shaking_lottery',
                'body': {"riskInformation": {"platform": 1, "pageClickKey": "",
                                             "eid": "DJW4Z53I6AVN6TDRH6CP7Z5GRBBAB5O3SGO6CLBB45KIFKTXMLMSYHGAYAZEZ5I3Y2GGJSETFIOHHGT63CU73AH6RQ",
                                             "fp": "3845343be8bb2f08e652a8a5b01eadc7",
                                             "shshshfp": "5ac8c64fcd5fc8db33274d052baa4031",
                                             "shshshfpa": "a3099d6c-9f0e-4abb-cbb6-43329642c546-1641185949",
                                             "shshshfpb": "rFnTG_ddkTSznPkjq0bQVIg"}},
                'h5st': '20220418141804569;7845056923415477;ae692;tk02w98b81bcc18nI2u56hz3AUJtULxULJrBwboCQAycYii9Ti4c+dV4FFioiMJHF+Ftr4kdFxEmCXpU4V6Zxe0gJArO;10acfd6014285d0be3175f7b811c6ab0f76bbda3011eba74d933d772afc3d1af;3.0;1650262684569'
            }
            res = await self.request(session, params, self.METHOD_POST)
            if res.get('success', False):
                if res['data']['lotteryType'] == 2:  # 优惠券
                    coupon_info = res['data']['couponInfo']
                    discount = coupon_info['couponDiscount']
                    quota = coupon_info['couponQuota']
                    limit_str = coupon_info['limitStr']
                    self.print('获得满{}减{}优惠券, {}'.format( quota, discount, limit_str))
                    self.coupon_list.append('获得满{}减{}优惠券, {}'.format(quota, discount, limit_str))

                elif res['data']['lotteryType'] == 5:  # 未中奖
                    self.print('未中奖, 提升京享值可以提高中奖几率和京豆中奖数量!')

                elif res['data']['lotteryType'] == 0:  # 京豆奖励
                    self.print(' 获得{}京豆'.format(res['data']['rewardBeanAmount']))
                    self.bean_count += res['data']['rewardBeanAmount']
                else:
                    self.print('获得:{}'.format(res['data']))
                await asyncio.sleep(1)
            else:
                self.print('摇盒子失败: {}'.format(res['resultTips']))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.daily_sign(session)
            await self.do_tasks(session)
            shake_times = await self.get_shake_times(session)
            await self.do_shake(session, shake_times)


if __name__ == '__main__':
    run_jd(JdShakeBean)
