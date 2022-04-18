#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_gold_creator.py
# @Time    : 2022/4/18 12:27 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 20 9 * * *
# @Desc    : 金榜创造营
import asyncio
import json
import random
import re
from urllib.parse import quote

import aiohttp

from app.jd import JdApp, run_jd


class JdGoldCreator(JdApp):

    def __init__(self, **kwargs):
        super(JdGoldCreator, self).__init__(**kwargs)
        self.headers.update({
            'referer': 'https://h5.m.jd.com/babelDiy/Zeus/2H5Ng86mUJLXToEo57qWkJkjFPxw/index.html',
        })

    @property
    def app_name(self):
        """
        :return:
        """
        return "金榜创造营"

    async def request(self, session, function_id, body=None):
        try:
            if body is None:
                body = {}
            url = 'https://api.m.jd.com/client.action?functionId={}&body={}' \
                  '&appid=content_ecology&clientVersion=10.0.6&client=wh5' \
                  '&jsonp=jsonp_kr1mdm3p_12m_29&eufv=false'.format(function_id, quote(json.dumps(body)))
            response = await session.post(url=url)
            text = await response.text()
            temp = re.search(r'\((.*)\);', text).group(1)
            data = json.loads(temp)
            await asyncio.sleep(3)
            return data
        except Exception as e:
            self.print('获取数据失败:{}'.format(e.args))
            return None

    async def get_index_data(self, session):
        """
        获取获得首页数据
        :param session:
        :return:
        """
        return await self.request(session, 'goldCreatorTab', {"subTitleId": "", "isPrivateVote": "0"})

    async def do_vote(self, session):
        """
        进行投票
        :param session:
        :return:
        """
        self.print('正在获取投票主题...')
        data = await self.get_index_data(session)
        if not data or data['code'] != '0':
            self.print('获取数据失败!')
            return
        subject_list = data['result']['subTitleInfos']
        stage_id = data['result']['mainTitleHeadInfo']['stageId']
        for subject in subject_list:
            if 'taskId' not in subject:
                continue
            if subject['hasVoted'] == '1':
                self.print('主题:《{}》已完成投票!'.format(subject['shortTitle']))
                continue
            body = {
                "groupId": subject['matGrpId'],
                "stageId": stage_id,
                "subTitleId": subject['subTitleId'],
                "batchId": subject['batchId'],
                "skuId": "",
                "taskId": int(subject['taskId']),
            }
            res = await self.request(session, 'goldCreatorDetail', body)
            if res['code'] != '0':
                self.print('获取主题:《{}》商品列表失败!'.format(subject['shortTitle']))
            else:
                self.print('获取主题:《{}》商品列表成功, 开始投票!'.format(subject['shortTitle']))

            await asyncio.sleep(2)

            task_list = res['result']['taskList']
            sku_list = res['result']['skuList']
            item_id = res['result']['signTask']['taskItemInfo']['itemId']
            sku = random.choice(sku_list)
            body = {
                "stageId": stage_id,
                "subTitleId": subject['subTitleId'],
                "skuId": sku['skuId'],
                "taskId": int(subject['taskId']),
                "itemId": item_id,
                "rankId": sku["rankId"],
                "type": 1,
                "batchId": subject['batchId'],
            }
            res = await self.request(session, 'goldCreatorDoTask', body)

            if res['code'] != '0':
                self.print('为商品:《{}》投票失败!'.format(sku['name']))
            else:
                if 'lotteryCode' in res['result'] and res['result']['lotteryCode'] != '0':
                    self.print('为商品:《{}》投票失败, {}'.format(sku['name'], res['result']['lotteryMsg']))
                elif 'taskCode' in res['result'] and res['result']['taskCode'] == '103':
                    self.print('为商品: 《{}》投票失败, {}!'.format(sku['name'], res['result']['taskMsg']))
                else:
                    self.print('为商品:《{}》投票成功, 获得京豆:{}'.format(sku['name'], res['result']['lotteryScore']))

            for task in task_list:
                if task[0]['taskStatus'] == 2:
                    continue
                body = {
                    "taskId": int(task[0]['taskId']),
                    "itemId": task[0]['taskItemInfo']['itemId'],
                    "type": 2,
                    "batchId": subject['batchId']
                }
                res = await self.request(session, 'goldCreatorDoTask', body)

                self.print('做额外任务: 《{}》, 结果:{}!'.format(task[0]['taskItemInfo']['title'], res))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_vote(session)  # 投票


if __name__ == '__main__':
    run_jd(JdGoldCreator)
