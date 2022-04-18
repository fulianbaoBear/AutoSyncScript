#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_farm.py
# @Time    : 2022/4/15 2:55 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 15 6,12,18 * * *
# @Desc    : 东东农场
import asyncio
import json
import time
from datetime import datetime
from urllib.parse import quote
import aiohttp
from app.jd import JdApp, run_jd


class JdFarm(JdApp):
    """
    东东农场
    """

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super(JdFarm, self).__init__(**kwargs)
        self.headers.update({
            'origin': 'https://carry.m.jd.com',
            'referer': 'https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html'
        })

    @property
    def app_name(self):
        """
        :return:
        """
        return "东东农场"

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param body:
        :param function_id:
        :return:
        """
        try:
            if not body:
                body = dict()
            if 'version' not in body:
                body['version'] = 13
            if 'channel' not in body:
                body['channel'] = 1

            url = 'https://api.m.jd.com/client.action?functionId={}&body={}&appid=wh5'.format(function_id,
                                                                                              quote(json.dumps(body)))
            response = await session.get(url=url)
            data = await response.json()
            await asyncio.sleep(1)
            return data
        except Exception as e:
            self.print('获取服务器数据错误:{}'.format(e.args))

    async def init_for_farm(self, session):
        """
        初始化农场数据
        :param session:
        :return:
        """
        data = await self.request(session, 'initForFarm')
        if data['code'] != '0' or 'farmUserPro' not in data:
            return None
        return data['farmUserPro']

    async def sign(self, session):
        """
        :param session:
        :return:
        """
        data = await self.request(session, 'signForFarm')
        if data['code'] == '0':
            self.print('签到成功, 已连续签到{}天!'.format(data['signDay']))
        elif data['code'] == '7':
            self.print('今日已签到过!')
        else:
            self.print('签到失败, {}'.format(data['message']))

        if 'todayGotWaterGoalTask' in data and data['todayGotWaterGoalTask']['canPop']:
            await asyncio.sleep(1)
            data = await self.request(session, 'gotWaterGoalTaskForFarm', {'type': 3})
            if data['code'] == '0':
                self.print('被水滴砸中, 获得{}g水滴!'.format(data['addEnergy']))

    async def do_browser_tasks(self, session, tasks):
        """
        做浏览任务
        :param tasks:
        :param session:
        :return:
        """
        for task in tasks:
            task_name = task['mainTitle']
            self.print('正在进行浏览任务: 《{}》...'.format(task_name))
            task_res = await self.request(session, 'browseAdTaskForFarm', {'advertId': task['advertId'], 'type': 0})
            # 完成任务去领取奖励
            if task_res['code'] == '0' or task_res['code'] == '7':
                task_award = await self.request(session, 'browseAdTaskForFarm',
                                                {'advertId': str(task['advertId']), 'type': 1})
                if task_award['code'] == '0':
                    self.print('成功领取任务:《{}》的奖励, 获得{}g水滴！'.format(task_name, task_award['amount']))
                else:
                    self.print('领取任务:《{}》的奖励失败, {}'.format(task_name, task_award))
            else:
                self.print('浏览任务:《{}》, 结果:{}'.format(task_name, task_res))

    async def get_encrypted_pin(self, session):
        """
        获取加密pin参数
        :return:
        """
        try:
            response = await session.get(
                'https://api.m.jd.com/client.action?functionId=getEncryptedPinColor&body=%7B%22version%22%3A14%2C'
                '%22channel%22%3A1%2C%22babelChannel%22%3A0%7D&appid=wh5')
            text = await response.text()
            data = json.loads(text)
            return data['result']
        except Exception as e:
            self.print('获取pin参数出错, {}'.format(e.args))

    async def timed_collar_drop(self, session):
        """
        定时领水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'gotThreeMealForFarm')
        if data['code'] == '0':
            self.print('【定时领水滴】获得 {}g!'.format(data['amount']))
        else:
            self.print('【定时领水滴】失败,{}!'.format(data))

    async def do_friend_water(self, session):
        """
        给好友浇水
        :param session:
        :return:
        """
        data = await self.request(session, 'friendListInitForFarm')
        if 'friends' not in data:
            self.print('获取好友列表失败!')
            return
        friends = data['friends']
        if len(friends) == 0:
            self.print('暂无好友!')
            return

        count = 0
        for friend in friends:
            if friend['friendState'] != 1:
                continue
            count += 1
            res = await self.request(session, 'waterFriendForFarm', {'shareCode': friend['shareCode']})
            self.print('为第{}个好友({})浇水, 结果：{}'.format(count, friend['nickName'], count, res))
            if res['code'] == '11' or count > 2:
                self.print('水滴不够, 退出浇水!')
                return

    async def clock_in(self, session):
        """
        打卡领水
        :param session:
        :return:
        """
        self.print('开始打卡领水活动(签到, 关注)')
        res = await self.request(session, 'clockInInitForFarm')
        if res['code'] == '0':
            if not res['todaySigned']:
                self.print('开始今日签到!')
                data = await self.request(session, 'clockInForFarm', {'type': 1})
                self.print('打卡结果{}'.format(data))
                if data['signDay'] == 7:
                    self.print('开始领取--惊喜礼包!')
                    gift_data = await self.request(session, 'clockInForFarm', {"type": 2})
                    self.print('惊喜礼包获得{}g水滴!'.format(gift_data['amount']))

        if res['todaySigned'] and res['totalSigned'] == 7:  # 签到七天领惊喜礼包
            self.print('开始领取--惊喜礼包!')
            gift_data = await self.request(session, 'clockInForFarm', {"type": 2})
            if gift_data['code'] == '7':
                self.print('领取惊喜礼包失败, 已领取过!')
            elif gift_data['code'] == '0':
                self.print('惊喜礼包获得{}g水滴!'.format(gift_data['amount']))
            else:
                self.print('领取惊喜礼包失败, 原因未知!')

        if res['themes'] and len(res['themes']) > 0:  # 限时关注得水滴
            for item in res['themes']:
                if not item['hadGot']:
                    self.print('关注ID：{}'.format(item['id']))
                    data1 = await self.request(session, 'clockInFollowForFarm', {
                        'id': str(item['id']),
                        'type': 'theme',
                        'step': 1
                    })
                    if data1['code'] == '0':
                        data2 = await self.request(session, 'clockInFollowForFarm', {
                            'id': item['id'],
                            'type': 'theme',
                            'step': 2
                        })
                        if data2['code'] == '0':
                            self.print('关注{}, 获得水滴{}g'.format(item['id'], data2['amount']))
        self.print('结束打卡领水活动(签到, 关注)...')

    async def water_drop_rain(self, session, task):
        """
        :param task:
        :param session:
        :return:
        """
        if task['f']:
            self.print('两次水滴雨任务已全部完成!')
            return

        if task['lastTime'] and int(time.time() * 1000) < task['lastTime'] + 3 * 60 * 60 * 1000:
            self.print('第{}次水滴雨未到时间:{}!'.format(task['winTimes'] + 1,
                                                datetime.fromtimestamp(int((task['lastTime']
                                                                            + 3 * 60 * 60 * 1000) / 1000))))
            return

        for i in range(task['config']['maxLimit']):
            data = await self.request(session, 'waterRainForFarm')
            if data['code'] == '0':
                self.print('第{}次水滴雨获得水滴:{}g'.format(task['winTimes'] + 1, data['addEnergy']))
            else:
                self.print('第{}次水滴雨执行错误:{}'.format(task['winTimes'] + 1, data))

    async def get_extra_award(self, session):
        """
        领取额外奖励
        :return:
        """
        for i in range(5):
            award_res = await self.request(session, 'receiveStageEnergy')
            if award_res['code'] == '0':
                self.print('成功领取好友助力奖励, {}g水滴!'.format(award_res['amount']))
            else:
                self.print('领取好友助力奖励失败, {}'.format(award_res))
                break
            await asyncio.sleep(2)

    async def turntable(self, session):
        """
        天天抽奖
        :return:
        """
        data = await self.request(session, 'initForTurntableFarm')
        if data['code'] != '0':
            self.print('当前无法参与天天抽奖!')
            return

        if not data['timingGotStatus']:
            if data['sysTime'] > (data['timingLastSysTime'] + 60 * 60 * data['timingIntervalHours'] * 1000):
                res = await self.request(session, 'timingAwardForTurntableFarm')
                self.print('领取定时奖励结果:{}'.format(res))
            else:
                self.print('免费赠送的抽奖机会未到时间!')
        else:
            self.print('4小时候免费赠送的抽奖机会已领取!')

        if 'turntableBrowserAds' in data and len(data['turntableBrowserAds']) > 0:
            count = 1
            for item in data['turntableBrowserAds']:
                if item['status']:
                    self.print('天天抽奖任务:{}, 今日已完成过!'.format(item['main']))
                    continue
                res = await self.request(session, 'browserForTurntableFarm', {'type': 1, 'adId': item['adId']})
                self.print('完成天天抽奖任务:《{}》, 结果:{}'.format(item['main'], res))
                await asyncio.sleep(1)
                award_res = await self.request(session, 'browserForTurntableFarm', {'type': 2, 'adId': item['adId']})
                self.print('领取天天抽奖任务:《{}》奖励, 结果:{}'.format(item['main'], award_res))
                count += 1

        await asyncio.sleep(1)
        data = await self.request(session, 'initForTurntableFarm')
        lottery_times = data['remainLotteryTimes']

        if lottery_times == 0:
            self.print('天天抽奖次数已用完, 无法抽奖！')
            return

        self.print('开始天天抽奖, 次数:{}'.format(lottery_times))

        for i in range(1, lottery_times + 1):
            res = await self.request(session, 'lotteryForTurntableFarm')
            self.print('第{}次抽奖结果:{}'.format(i, res))
            await asyncio.sleep(1)

    async def dd_park(self, session):
        """
        :param session:
        :return:
        """
        data = await self.request(session, 'ddnc_farmpark_Init', {"version": "1", "channel": 1})
        if data['code'] != '0' or 'buildings' not in data:
            self.print('无法获取东东乐园任务！')
            return
        item_list = data['buildings']

        for idx in range(len(item_list)):
            item = item_list[idx]
            if 'topResource' not in item or 'task' not in item['topResource']:
                continue
            task = item['topResource']['task']
            if task['status'] != 1:
                self.print('今日已完成东东乐园:{} 浏览任务!'.format(item['name']))
                continue
            else:
                res = await self.request(session, 'ddnc_farmpark_markBrowser', {
                    "version": "1",
                    "channel": 1,
                    "advertId": task['advertId']})
                if res['code'] != '0':
                    self.print('无法进行东东乐园:{} 浏览任务, 原因:{}'.format(item['name'], res['message']))
                    continue
                self.print('正在进行东东乐园:{} 浏览任务!'.format(item['name'], task['browseSeconds']))
                await asyncio.sleep(1)
                res = await self.request(session, 'ddnc_farmpark_browseAward', {
                    "version": "1",
                    "channel": 1,
                    "advertId": task['advertId'],
                    "index": idx,
                    "type": 1
                })
                if res['code'] == '0':
                    self.print('领取东东乐园:{} 浏览任务奖励成功, 获得{}g水滴!'.format(item['name'],
                                                                     res['result']['waterEnergy']))
                else:
                    self.print('领取东东乐园:{} 浏览任务奖励失败, {}!'.format(item['name'], res['message']))

    async def do_daily_task(self, session):
        """
        领水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'taskInitForFarm')
        if data['code'] != '0':
            self.print('获取领水滴任务列表失败!')
            return
        today_signed = data['signInit']['todaySigned']

        if not today_signed:  # 签到任务
            await self.sign(session)
        else:
            self.print('今日已签到, 已连续签到{}天!'.format(data['signInit']['totalSigned']))

        if not data['gotBrowseTaskAdInit']['f']:  # 浏览任务
            tasks = data['gotBrowseTaskAdInit']['userBrowseTaskAds']
            await self.do_browser_tasks(session, tasks)
        else:
            self.print('今日浏览广告任务已完成!')

        if not data['gotThreeMealInit']['f']:  # 定时领水
            await self.timed_collar_drop(session)

        if not data['waterFriendTaskInit']['f'] and \
                data['waterFriendTaskInit']['waterFriendCountKey'] < data['waterFriendTaskInit']['waterFriendMax']:
            await self.do_friend_water(session)

        await self.clock_in(session)  # 打卡领水

        await self.water_drop_rain(session, data['waterRainInit'])  # 水滴雨

        await self.get_extra_award(session)

        await self.turntable(session)

        await self.dd_park(session)  # 东东乐园浏览领水滴

    async def get_stage_award(self, session, water_result):
        """
        领取浇水阶段性奖励
        :param session:
        :param water_result: 浇水返回的结果
        :return:
        """
        if water_result['waterStatus'] == 0 and water_result['treeEnergy'] == 10:
            award_res = await self.request(session, 'gotStageAwardForFarm', {'type': '1'})
            self.print('领取浇水第一阶段奖励:{}'.format(award_res))

        elif water_result['waterStatus'] == 1:
            award_res = await self.request(session, 'gotStageAwardForFarm', {'type': '2'})
            self.print('领取浇水第二阶段奖励:{}'.format(award_res))
        elif water_result['waterStatus'] == 2:
            award_res = await self.request(session, 'gotStageAwardForFarm', {'type': '3'})
            self.print('领取浇水第三阶段奖励:{}'.format(award_res))

    async def do_ten_water(self, session):
        """
        浇水10次
        :param session:
        :return:
        """
        card_data = await self.request(session, 'myCardInfoForFarm')

        task_data = await self.request(session, 'taskInitForFarm')

        task_limit_times = task_data['totalWaterTaskInit']['totalWaterTaskLimit']
        cur_times = task_data['totalWaterTaskInit']['totalWaterTaskTimes']

        if cur_times == task_limit_times:
            self.print('今日已完成十次浇水!'.format(self.account))
            return

        fruit_finished = False  # 水果是否成熟

        for i in range(cur_times, task_limit_times):
            self.print('开始第{}次浇水!'.format(i + 1))
            res = await self.request(session, 'waterGoodForFarm')
            if res['code'] != '0':
                self.print('浇水异常, 退出浇水!')
                break
            self.print('剩余水滴:{}g!'.format(res['totalEnergy']))
            fruit_finished = res['finished']
            if fruit_finished:
                break
            if res['totalEnergy'] < 10:
                self.print('水滴不够10g, 退出浇水!')
                break
            await self.get_stage_award(session, res)
            await asyncio.sleep(1)

        if fruit_finished:
            self.print('水果已可领取!')

    async def get_first_water_award(self, session):
        """
        领取首次浇水奖励
        :return:
        """
        task_data = await self.request(session, 'taskInitForFarm')

        if not task_data['firstWaterInit']['f'] and task_data['firstWaterInit']['totalWaterTimes'] > 0:
            res = await self.request(session, 'firstWaterTaskForFarm')
            if res['code'] == '0':
                self.print('【首次浇水奖励】获得{}g水滴!'.format(res['amount']))
            else:
                self.print('【首次浇水奖励】领取失败, {}'.format(res))
        else:
            self.print('首次浇水奖励已领取!')

    async def get_ten_water_award(self, session):
        """
        获取十次浇水奖励
        :param session:
        :return:
        """
        task_data = await self.request(session, 'taskInitForFarm')
        task_limit_times = task_data['totalWaterTaskInit']['totalWaterTaskLimit']
        cur_times = task_data['totalWaterTaskInit']['totalWaterTaskTimes']
        if not task_data['totalWaterTaskInit']['f'] and cur_times >= task_limit_times:
            res = await self.request(session, 'totalWaterTaskForFarm')
            if res['code'] == '0':
                self.print('【十次浇水奖励】获得{}g水滴!'.format(res['totalWaterTaskEnergy']))
            else:
                self.print('【十次浇水奖励】领取失败, {}'.format(res))

        elif cur_times < task_limit_times:
            self.print('【十次浇水】任务未完成, 今日浇水:{}'.format(cur_times))
        else:
            self.print('【十次浇水】奖励已领取!')

    async def get_water_friend_award(self, session):
        """
        领取给2未好友浇水的奖励
        :param session:
        :return:
        """
        task_data = await self.request(session, 'taskInitForFarm')
        water_friend_task_data = task_data['waterFriendTaskInit']

        if water_friend_task_data['waterFriendGotAward']:
            self.print('今日已领取给2位好友浇水任务奖励!')
            return

        if water_friend_task_data['waterFriendCountKey'] >= water_friend_task_data['waterFriendMax']:
            res = await self.request(session, 'waterFriendGotAwardForFarm')
            if res['code'] == '0':
                self.print('领取给2位好友浇水任务奖励成功, 获得{}g水滴!'.format(res['addWater']))
            else:
                self.print('领取给2位好友浇水任务失败, {}'.format(res))

    async def click_duck(self, session):
        """
        点鸭子任务
        :return:
        """
        for i in range(10):
            data = await self.request(session, 'getFullCollectionReward', {"type": 2, "version": 14, "channel": 1,
                                                                           "babelChannel": 0})
            if data['code'] == '0':
                self.print('{}'.format(data['title']))
            else:
                self.print('点鸭子次数已达上限!')
                break

    async def do_ten_water_again(self, session):
        """
        再次进行十次浇水
        :param session:
        :return:
        """
        data = await self.request(session, 'initForFarm')
        total_energy = data['farmUserPro']['totalEnergy']
        self.print('剩余{}g水滴!'.format(total_energy))
        card_data = await self.request(session, 'myCardInfoForFarm')
        bean_card, sign_card = card_data['beanCard'], card_data['signCard'],
        double_card, fast_card = card_data['doubleCard'], card_data['fastCard']
        self.print('背包已有道具:\n  快速浇水卡: {}\n  水滴翻倍卡:{}\n  水滴换豆卡:{}'
                   '\n  加签卡:{}'.format(fast_card, double_card, bean_card, sign_card))

        if total_energy > 100 and double_card > 0:
            for i in range(double_card):
                res = await self.request(session, 'userMyCardForFarm', {'cardType': 'doubleCard'})
                self.print('使用水滴翻倍卡结果:{}'.format(res))

        if sign_card > 0:
            for i in range(sign_card):
                res = await self.request(session, 'userMyCardForFarm', {'cardType': 'signCard'})
                self.print('使用加签卡结果:{}'.format(res))

        data = await self.request(session, 'initForFarm')
        total_energy = data['farmUserPro']['totalEnergy']

        jd_farm_retain_water = 80
        #  可用水滴
        available_water = total_energy - jd_farm_retain_water

        if available_water < 10:
            self.print('当前可用水滴(=当前剩余水滴{}g-保留水滴{}g)不足10g, 无法浇水!'.format(total_energy,
                                                                       jd_farm_retain_water))
            return

        for i in range(int(available_water / 10)):
            res = await self.request(session, 'waterGoodForFarm')
            if res['code'] == '0':
                self.print('成功浇水10g...')
                if res['finished']:  # 水果成熟了不需要再浇水
                    break
            else:
                self.print('浇水失败, 不再浇水!')
                break

    async def got_water(self, session):
        """
        领取水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'gotWaterGoalTaskForFarm',
                                  {"type": 3, "version": 14, "channel": 1, "babelChannel": 0})
        self.print('领取水滴:{}!'.format(data))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            farm_info = await self.init_for_farm(session=session)
            if not farm_info:
                self.print('无法获取农场数据, 退出程序!')
                return
            await self.do_daily_task(session)  # 每日任务
            await self.do_ten_water(session)  # 浇水十次
            await self.get_first_water_award(session)  # 领取首次浇水奖励
            await self.get_ten_water_award(session)  # 领取十次浇水奖励
            await self.get_water_friend_award(session)  # 领取给好友浇水的奖励
            await self.click_duck(session)  # 点鸭子任务
            await self.do_ten_water_again(session)  # 再次浇水
            await self.got_water(session)  # 领水滴


if __name__ == '__main__':
    run_jd(JdFarm)
