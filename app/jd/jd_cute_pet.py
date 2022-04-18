#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_cute_pet.py
# @Time    : 2022/4/18 11:49 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 8 7,13,19 * * *
# @Desc    : 东东萌宠
import asyncio
import json
from datetime import datetime
from urllib.parse import quote

import aiohttp

from app.jd import JdApp, run_jd


class JdCutPet(JdApp):
    
    def __init__(self, **kwargs):
        super(JdCutPet, self).__init__(**kwargs)
        self.headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-requested-with': 'com.jingdong.app.mall',
            'sec-fetch-mode': 'cors',
            'origin': 'https://carry.m.jd.com',
            'sec-fetch-site': 'same-site',
            'referer': 'https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html'
    })
        
    @property
    def app_name(self):
        """
        :return: 
        """
        return "东东萌宠"
    
    async def request(self, session, function_id, body=None, wait_time=3):
        """
        :param wait_time:
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}
        body["version"] = 2
        body["channel"] = 'app'
        url = 'https://api.m.jd.com/client.action?functionId={}' \
              '&body={}&appid=wh5&loginWQBiz=pet-town&clientVersion=9.0.4'.format(function_id, quote(json.dumps(body)))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            if data['code'] != '0':
                return {
                    'resultCode': '-500',
                    'message': '获取数据失败!',
                }
            elif data['resultCode'] != '0':
                return data
            else:
                data['result']['resultCode'] = '0'
                return data['result']

        except Exception as e:
            self.print('访问服务器异常:{}!'.format(e.args))
    
    async def init(self, session):
        """
        初始化
        :return:
        """
        self.print('{}, 正在初始化数据...'.format(self.account))
        data = await self.request(session, 'initPetTown')
        if data['resultCode'] != '0':
            self.print('{}, 无法获取活动首页数据, {}!'.format(self.account, data['message']))
            return False

        if data['userStatus'] == 0:
            self.print('萌宠活动未开启, 请手动去京东APP开启活动入口：我的->游戏与互动->查看更多开启！')

        if 'goodsInfo' not in data:
            self.print('暂未选购商品!'.format(self.account))

        if data['petStatus'] == 5:
            self.print('已可兑换商品!'.format(self.account))

        if data['petStatus'] == 6:
            self.print('已领取红包, 但未继续领养新的物品!'.format(self.account))

        return True
    
    async def get_task_list(self, session):
        """
        获取任务列表
        :param session:
        :return:
        """
        data = await self.request(session, 'taskInit', {'version': 1})
        if data['resultCode'] != '0':
            self.print(' 获取任务列表失败!')
            return []
        task_list = dict()

        for key in data['taskList']:
            task_list[key] = data[key]

        return task_list
    
    async def sign(self, session, task):
        """
        签到任务
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            self.print('{}, 今日已完成签到!'.format(self.account))
            return
        data = await self.request(session, 'getSignReward')

        if data['resultCode'] != '0':
            self.print('签到失败!')
        else:
            self.print('签到成功, 获得狗粮: {}g!'.format(data['signReward']))
    
    async def first_feed(self, session, task):
        """
        首次喂食
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            self.print('今日已完成首次喂食任务!')
            return

        data = await self.request(session, 'feedPets')

        if data['resultCode'] != '0':
            self.print('首次喂食任务失败!')
        else:
            self.print('完成首次喂食任务, 获得狗粮: {}g!'.format(data['firstFeedReward']))
    
    async def three_meal(self, session, task):
        """
        每日三餐开福袋
        :param session:
        :param task:
        :return:
        """
        cur_hour = datetime.now().hour
        can_do = False

        for i in range(len(task['threeMealTimes'])):
            item_range = [int(n) for n in task['threeMealTimes'][i].split('-')]
            if item_range[0] <= cur_hour <= item_range[1]:
                can_do = True

        if not can_do or task['finished']:
            self.print('当前不在每日三餐任务时间范围内或者任务已完成!')
            return

        data = await self.request(session, 'getThreeMealReward')

        if data['resultCode'] != '0':
            self.print('每日三餐任务完成失败!')
        else:
            self.print('完成每日三餐任务成功, 获得狗粮:{}g!'.format(data['threeMealReward']))
    
    async def feed_food_again(self, session):
        """
        再次喂食
        :param session:
        :return:
        """
        self.print('再次进行喂食!')
        data = await self.request(session, 'initPetTown')
        if data['resultCode'] != '0':
            self.print('获取活动数据失败!')
            return

        food_amount = data.get('foodAmount', 0)  # 狗粮总数
        keep_amount = 80  # 保留80狗粮用于完成明天的10次喂食任务

        if (int(food_amount) - keep_amount) > 10:
            times = int((int(food_amount) - keep_amount) / 10)

            for i in range(times):
                self.print('正在进行第{}次喂食!'.format(i+1))
                data = await self.request(session, 'feedPets')
                if data['resultCode'] != '0':
                    self.print('第{}次喂食失败, 停止喂食!'.format(i+1))
                else:
                    self.print('第{}次喂食成功!'.format(i+1))
        else:
            self.print('当前狗粮(剩余狗粮{}-保留狗粮{})不足10g ,无法喂食!'.format(food_amount, keep_amount))

    async def feed_reach_hundred(self, session, task):
        """
        每日喂食到100g狗粮
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            self.print('{}, 今日已完成喂狗粮{}g任务!'.format(self.account, task['feedReachAmount']))
            return

        had_feed_count = int(task['hadFeedAmount'] / 10)
        need_feed_count = int(task['feedReachAmount'] / 10)

        self.print('当前喂食任务进度:{}/{}!'.format(had_feed_count, need_feed_count))

        for i in range(had_feed_count, need_feed_count):
            data = await self.request(session, 'feedPets')

            if data['resultCode'] != '0':
                if data['resultCode'] == '3003':
                    self.print('第{}次喂食失败!, 狗粮剩余不足，退出喂食!'.format(i+1))
                    break
                else:
                    self.print('第{}次喂食失败!'.format(i + 1))
            else:
                self.print(' 第{}次喂食成功, 进度:{}/{}!'.format(i + 1, i + 1, need_feed_count))

    async def browser_task(self, session, task):
        """
        浏览任务
        :param session:
        :param task:
        :return:
        """
        if task['finished']:
            self.print('{}, 今日已完成浏览任务:{}!'.format(self.account, task['title']))
            return

        body = {
            "index": task['index'], "version": 1, "type": 1
        }
        data = await self.request(session, 'getSingleShopReward', body)

        if data['resultCode'] != '0':
            if data['resultCode'] == '5000':
                self.print('已领取浏览任务:{}!'.format( task['title']))
            else:
                self.print('领取浏览任务:{}失败!'.format( task['title']))
                return
        else:
            self.print('领取浏览任务:{}成功!'.format(task['title']))

        body = {
            "index": task['index'], "version": 1, "type": 2
        }
        data = await self.request(session, 'getSingleShopReward', body)

        if data['resultCode'] != '0':
            self.print('完成浏览任务:{}失败!'.format( task['title']))
        else:
            self.print('完成浏览任务:{}成功, 获得{}g狗粮!'.format(task['title'], data['reward']))

    async def do_tasks(self, session, task_list):
        """
        做任务
        :param session:
        :param task_list:
        :return:
        """
        func_map = {
            'signInit': self.sign,  # 签到
            'firstFeedInit': self.first_feed,  # 首次喂食
            'threeMealInit': self.three_meal,  # 三餐
            'feedReachInit': self.feed_reach_hundred,  # 投喂百次
            'browseSingleShopInit': self.browser_task,  # 浏览任务
        }
        for key, task in task_list.items():
            if 'browseSingleShopInit' in key:
                await func_map['browseSingleShopInit'](session, task)
            else:
                await func_map[key](session, task)

    async def pet_sport(self, session):
        """
        遛狗10次
        :param session:
        :return:
        """
        times = 0
        self.print('{}, 正在遛狗...'.format(self.account))
        while True:
            times += 1
            data = await self.request(session, 'petSport')

            if data['resultCode'] != '0':
                if data['resultCode'] == '1013':
                    self.print('第{}次遛狗失败, 有未领取奖励, 去领取!'.format(times))
                elif data['resultCode'] == '3001':
                    self.print('第{}次遛狗失败, 达到宠物运动次数上限!'.format(times))
                    break
                else:
                    self.print('第{}次遛狗失败, 结束遛狗!'.format(times))
                    break
            food_reward = data['foodReward']

            self.print('完成一次遛狗, 正在领取遛狗奖励!')

            data = await self.request(session, 'getSportReward')

            if data['resultCode'] != '0':
                self.print('领取第{}次遛狗奖励失败, 结束遛狗!'.format(times))
            else:
                self.print('成功领取第{}次遛狗奖励, 获得狗粮:{}g, 当前狗粮:{}g!'.format(times, food_reward, data['foodAmount']))
    
    async def collect_energy(self, session):
        """
        收取好感度
        :param session:
        :return:
        """
        self.print('正在收取好感度...')

        data = await self.request(session, 'energyCollect')
        if data['resultCode'] != '0':
            self.print('收取好感度失败!')
            return

        message = '【第{}块勋章完成进度】{}%，' \
                  '还需收集{}好感度!\n'.format(data['medalNum'] + 1, data['medalPercent'], data['needCollectEnergy'])
        message += '【已获得勋章】{}块，还需收集{}块即可兑换奖品!\n'.format(data['medalNum'], data['needCollectMedalNum'])

        self.print('收集好感度成功!{}'.format(message))
    
    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            is_success = await self.init(session)
            if not is_success:
                self.print('{}, 初始化失败, 退出程序!'.format(self.account))
                return
            task_list = await self.get_task_list(session)
            await self.do_tasks(session, task_list)
            await self.pet_sport(session)
            await self.feed_food_again(session)  # 再次喂食
            await self.collect_energy(session)


if __name__ == '__main__':
    run_jd(JdCutPet)
