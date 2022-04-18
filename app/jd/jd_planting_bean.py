#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_planting_bean.py
# @Time    : 2022/4/18 1:43 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 18 6,12,18 * * *
# @Desc    : 种豆得豆
import asyncio
import json
import re
from urllib.parse import quote

import aiohttp
import moment

from app.jd import JdApp, run_jd


class JdPlantingBean(JdApp):
    
    def __init__(self, **kwargs):
        super(JdPlantingBean, self).__init__(**kwargs)
        self.headers.update({
            "Host": "api.m.jd.com",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        self.cur_round_id = None  # 本期活动id
        self.prev_round_id = None  # 上期活动id
        self.next_round_id = None  # 下期活动ID
        self.cur_round_list = None
        self.prev_round_list = None
        self.task_list = None  # 任务列表
        self.nickname = None  # 京东昵称
        
    @property
    def app_name(self):
        return "种豆得豆"
    
    async def post(self, session, function_id, params=None):
        """
        :param session:
        :param function_id:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        params['version'] = '9.2.4.0'
        params['monitor_source'] = 'plant_app_plant_index'
        params['monitor_refer'] = ''

        url = 'https://api.m.jd.com/client.action'

        body = f'functionId={function_id}&body={quote(json.dumps(params))}&appid=ld' \
               f'&client=apple&area=19_1601_50258_51885&build=167490&clientVersion=9.3.2'

        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            await asyncio.sleep(1)
            data = json.loads(text)
            return data

        except Exception as e:
            self.print('访问服务器失败:[function_id={}], 错误信息:{}'.format(function_id, e.args))

    async def get(self, session, function_id, body=None, wait_time=1):
        """
        :param wait_time:
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}

        try:
            body["version"] = "9.2.4.0"
            body["monitor_source"] = "plant_app_plant_index"
            body["monitor_refer"] = ""

            url = f'https://api.m.jd.com/client.action?functionId={function_id}&body={quote(json.dumps(body))}&appid=ld'
            response = await session.get(url=url)
            text = await response.text()
            data = json.loads(text)
            if wait_time > 0:
                await asyncio.sleep(1)
            return data

        except Exception as e:
            self.print('访问服务器失败:[function_id={}], 错误信息:{}'.format(function_id, e.args))

    async def planting_bean_index(self, session):
        """
        :return:
        """
        data = await self.post(session=session, function_id='plantBeanIndex')

        if not data or data['code'] != '0' or 'errorMessage' in data:
            self.print('访问首页失败, 退出程序！错误原因:{}'.format(data))
            return False
        data = data['data']

        round_list = data['roundList']
        cur_idx = 2
        prev_idx = 1
        prev_start_date = moment.date('01-01')
        for i in range(len(round_list)):
            rnd = round_list[i]
            if '本期' in rnd['dateDesc']:
                cur_idx = i
                break
            elif '上期' in rnd['dateDesc']:
                temp = re.search('-(\d+月\d+)日', rnd['dateDesc']).group(1).replace('月', '-')
                prev_date = moment.date(temp)
                if prev_date > prev_start_date:
                    prev_start_date = prev_date
                    prev_idx = i

        self.cur_round_id = round_list[cur_idx]['roundId']
        self.task_list = data['taskList']
        self.cur_round_list = round_list[cur_idx]
        self.prev_round_list = round_list[prev_idx]
        self.message = '\n【活动名称】种豆得豆\n'
        self.message += f"【京东昵称】:{data['plantUserInfo']['plantNickName']}\n"
        self.message += f'【上期时间】:{round_list[prev_idx]["dateDesc"].replace("上期 ", "")}\n'
        self.message += f'【上期成长值】:{round_list[prev_idx]["growth"]}\n'
        return True

    async def receive_nutrient(self, session):
        """
        收取营养液
        :param session:
        :return:
        """
        self.print('开始收取营养液!')
        data = await self.post(session, 'receiveNutrients',
                               {"roundId": self.cur_round_id, "monitor_refer": "plant_receiveNutrients"})
        self.print('完成收取营养液, {}'.format(data))

    
    async def receive_nutrient_task(self, session, task):
        """
        :param session:
        :param task:
        :return:
        """
        params = {
            "monitor_refer": "plant_receiveNutrientsTask",
            "awardType": str(task['taskType'])
        }
        data = await self.get(session, 'receiveNutrientsTask', params)
        self.print('收取营养液:{}'.format(data))

    async def visit_shop_task(self, session, task):
        """
        浏览店铺任务
        :param session:
        :param task:
        :return:
        """
        shop_data = await self.get(session, 'shopTaskList', {"monitor_refer": "plant_receiveNutrients"})
        if shop_data['code'] != '0':
            self.print('获取{}任务失败!'.format(task['taskName']))

        shop_list = shop_data['data']['goodShopList'] + shop_data['data']['moreShopList']
        for shop in shop_list:
            body = {
                "monitor_refer": "plant_shopNutrientsTask",
                "shopId": shop["shopId"],
                "shopTaskId": shop["shopTaskId"]
            }
            data = await self.get(session, 'shopNutrientsTask', body)
            if data['code'] == '0' and 'data' in data:
                self.print('浏览店铺结果:{}'.format(data['data']))
            else:
                self.print('浏览店铺结果:{}'.format(data['errorMessage']))
            await asyncio.sleep(1)

    
    async def pick_goods_task(self, session, task):
        """
        挑选商品任务
        :return:
        """
        data = await self.get(session, 'productTaskList', {"monitor_refer": "plant_productTaskList"})

        for products in data['data']['productInfoList']:
            for product in products:
                body = {
                    "monitor_refer": "plant_productNutrientsTask",
                    "productTaskId": product['productTaskId'],
                    "skuId": product['skuId']
                }
                res = await self.get(session, 'productNutrientsTask', body)
                if 'errorCode' in res:
                    self.print('{}'.format(res['errorMessage']))
                else:
                    self.print('{}'.format(res))

                await asyncio.sleep(1)

    
    async def focus_channel_task(self, session, task):
        """
        关注频道任务
        :param session:
        :param task:
        :return:
        """
        data = await self.get(session, 'plantChannelTaskList')
        if data['code'] != '0':
            self.print('获取关注频道任务列表失败!')
            return
        data = data['data']
        channel_list = data['goodChannelList'] + data['normalChannelList']

        for channel in channel_list:
            body = {
                "channelId": channel['channelId'],
                "channelTaskId": channel['channelTaskId']
            }
            res = await self.get(session, 'plantChannelNutrientsTask', body)
            if 'errorCode' in res:
                self.print('关注频道结果:{}'.format(res['errorMessage']))
            else:
                self.print('关注频道结果:{}'.format(res))
            await asyncio.sleep(1)

    async def get_friend_nutriments(self, session, page=1):
        """
        获取好友营养液
        :param page:
        :param session:
        :return:
        """
        if page > 3:
            return
        self.print('{}, 开始收取第{}页的好友营养液!'.format(self.account, page))
        body = {
            'pageNum': str(page),
        }
        data = await self.post(session, 'plantFriendList', body)

        if data['code'] != '0' or 'data' not in data:
            self.print('无法获取好友列表!'.format(self.account))
            return

        data = data['data']
        msg = None

        if 'tips' in data:
            self.print('今日偷取好友营养液已达上限!')
            return
        if 'friendInfoList' not in data or len(data['friendInfoList']) < 0:
            self.print('当前暂无可以获取的营养液的好友！')
            return

        for item in data['friendInfoList']:
            if 'nutrCount' not in item or int(item['nutrCount']) <= 1:  # 小于两瓶基本无法活动奖励, 不收
                continue
            body = {
                'roundId': self.cur_round_id,
                'paradiseUuid': item['paradiseUuid']
            }
            res = await self.post(session, 'collectUserNutr', body)
            if res['code'] != '0' or 'errorMessage' in res:
                self.print('帮:{}收取营养液失败!'.format(item['plantNickName']))
                continue

            self.print(res['data']['collectMsg'])
            await asyncio.sleep(0.5)  # 短暂延时，避免出现活动火爆

        if not msg:
            self.print('第{}页好友没有可收取的营养液!'.format(page))

        await asyncio.sleep(1)
        await self.get_friend_nutriments(session, page+1)

    
    async def evaluation_goods_task(self, session, task):
        """
        :param session:
        :param task:
        :return:
        """
        self.print('任务:{}, 请手动前往APP完成任务！'.format(task['taskName']))

    
    async def visit_meeting_place_task(self, session, task):
        """
        逛会场
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '4'})
        self.print('{}:{}'.format(task['taskName'], data))

    
    async def free_fruit_task(self, session, task):
        """
        免费水果任务
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '36'})
        self.print('{}:{}'.format(task['taskName'], data))

    
    async def jx_red_packet(self, session, task):
        """
        京喜红包
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '33'})
        self.print('{}:{}'.format(task['taskName'], data))

    
    async def double_sign_task(self, session, task):
        """
        京喜双签
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '7'})
        self.print('{}:{}'.format(task['taskName'], data))

    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        task_map = {
            1: self.receive_nutrient_task,  # 每日签到
            # 2: self.help_friend_task,  # 助力好友
            3: self.visit_shop_task,  # 浏览店铺
            # 4: self.visit_meeting_place_task,  # 逛逛会场
            5: self.pick_goods_task,  # 挑选商品
            # 7: self.double_sign_task,  # 金融双签
            8: self.evaluation_goods_task,  # 评价商品,
            10: self.focus_channel_task,  # 关注频道,
            33: self.jx_red_packet,  # 京喜红包
            36: self.free_fruit_task  # 免费水果

        }
        for task in self.task_list:
            if task['isFinished'] == 1:
                self.print('任务:{}, 今日已领取过奖励, 不再执行...'.format(task['taskName']))
                continue
            if task['taskType'] in task_map:
                task['account'] = self.account
                await task_map[task['taskType']](session, task)
            else:
                data = await self.post(session, 'receiveNutrientsTask', {"awardType": str(task['taskType'])})
                self.print('{}:{}'.format(task['taskName'], data))

            await asyncio.sleep(0.2)

    async def collect_nutriments(self, session):
        """
        收取营养液
        :return:
        """
        # 刷新数据
        await self.planting_bean_index(session)
        await asyncio.sleep(0.1)
        if not self.cur_round_list or 'roundState' not in self.cur_round_list:
            self.print('获取营养池数据失败, 无法收取！'.format(self.account))

        if self.cur_round_list['roundState'] == '2':
            for item in self.cur_round_list['bubbleInfos']:
                body = {
                    "roundId": self.cur_round_id,
                    "nutrientsType": item['nutrientsType'],
                }
                res = await self.post(session, 'cultureBean', body)
                self.print('收取-{}-的营养液, 结果:{}'.format(item['name'], res))
                await asyncio.sleep(1)
            self.print('收取营养液完成！')
        else:
            self.print('暂无可收取的营养液!')

    async def get_reward(self, session):
        """
        获取奖励
        :param session:
        :return:
        """
        await self.planting_bean_index(session)
        await asyncio.sleep(0.2)
        if not self.prev_round_list:
            self.print('无法获取上期活动信息!')

        if self.prev_round_list['awardState'] == '6':
            self.message += '【上期兑换京豆】{}个!\n'.format(self.prev_round_list['awardBeans'])
        elif self.prev_round_list['awardState'] == '4':
            self.message += '【上期状态】{}\n'.format(self.prev_round_list['tipBeanEndTitle'])
        elif self.prev_round_list['awardState'] == '5':
            self.print('开始领取京豆!')
            body = {
                "roundId": self.prev_round_list['roundId']
            }
            res = await self.post(session, 'receivedBean', body)
            if res['code'] != '0':
                self.message += '【上期状态】查询异常:{}\n'.format(self.prev_round_list)
            else:
                self.message += '【上期兑换京豆】{}个\n'.format(res['data']['awardBean'])
        else:
            self.message += '【上期状态】查询异常:{}\n'.format(self.prev_round_list)

        self.message += f'【本期时间】:{self.cur_round_list["dateDesc"].replace("上期 ", "")}\n'
        self.message += f'【本期成长值】:{self.cur_round_list["growth"]}\n'
        print(self.message)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            is_success = await self.planting_bean_index(session)
            if not is_success:
                self.print('无法获取活动数据!')
                return

            await self.receive_nutrient(session)
            await self.do_tasks(session)
            await self.get_friend_nutriments(session)
            await self.collect_nutriments(session)
            await self.get_reward(session)


if __name__ == '__main__':
    run_jd(JdPlantingBean)
