#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd_unsubscribe.py
# @Time    : 2022/4/18 2:40 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : 50 23 * * *
# @Desc    : 取消商品关注/商品收藏
import asyncio
import json
import re
import time
from urllib.parse import urlencode

import aiohttp

from app.jd import JdApp, run_jd


class JdUnsubscribe(JdApp):
    
    def __init__(self, **kwargs):
        super(JdUnsubscribe, self).__init__(**kwargs)
        self.headers.update({
             'referer': 'https://wqs.jd.com/',
        })
    
    @property
    def app_name(self):
        return "取消商品关注/收藏"
    
    async def request(self, session, path, params=None, method='GET'):
        """
        请求服务器数据
        :param method:
        :param session:
        :param path:
        :param params:
        :return:
        """
        try:
            if not params:
                params = dict()
            params['lastlogintime'] = 0
            params['_'] = int(time.time()*1000)
            params['sceneval'] = 2
            params['g_login_type'] = 1
            params['g_ty'] = 'ls'
            params['callback'] = 'json'
            url = f'https://wq.jd.com/{path}?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)

            text = await response.text()

            temp = re.search('json\((.*)\);', text, re.S).group(1)
            data = json.loads(temp)
            return data
        except Exception as e:
            self.print('请求数据失败, {}'.format(e.args))
            return {
                'iRet': '999'
            }

    async def unsubscribe_goods(self, session):
        """
        取关商品
        :param session:
        :return:
        """
        max_page = 10
        cur_page = 1
        while True:
            comm_id_list = []
            if cur_page >= max_page:
                break
            params = {
                'cp': 1,
                'pageSize': 20,
                'category':    0,
                'promote':    0,
                'cutPrice':    0,
                'coupon':    0,
                'stock':    0,
            }
            data = await self.request(session, '/fav/comm/FavCommQueryFilter', params)
            if not data or data.get('iRet', '-1') != '0':
                break
            max_page = int(data.get('totalPage', '1'))
            cur_page = int(data.get('cp', '1'))

            for item in data.get('data', []):
                comm_id_list.append(item.get('commId'))

            if not comm_id_list:
                break

            cur_page += 1
            await asyncio.sleep(2)

            unfollow_path = '/fav/comm/FavCommBatchDel'
            unfollow_params = {
                'commId': ','.join(comm_id_list)
            }
            data = await self.request(session, unfollow_path, unfollow_params)

            if data.get('iRet', '-1') == '0':
                self.print('成功取关{}个商品！'.format(len(comm_id_list)))
            else:
                self.print(data)

            await asyncio.sleep(2)

    async def unsubscribe_shops(self, session):
        """
        取关店铺
        :param session:
        :return:
        """
        max_page = 10
        cur_page = 1
        while True:
            shop_id_list = []
            if cur_page > max_page:
                break
            params = {
                'cp': 1,
                'pageSize': 20
            }
            data = await self.request(session, '/fav/shop/QueryShopFavList', params)
            if not data or data.get('iRet', '-1') != '0':
                break
            max_page = int(data.get('totalPage', '1'))
            cur_page = int(data.get('cp', '1'))

            for item in data.get('data', []):
                shop_id_list.append(item.get('shopId'))

            if not shop_id_list:
                break

            cur_page += 1
            await asyncio.sleep(1.5)

            unfollow_path = '/fav/shop/batchunfollow'
            unfollow_params = {
                'shopId': ','.join(shop_id_list)
            }
            data = await self.request(session, unfollow_path, unfollow_params)

            if data.get('iRet', '-1') == '0':
                self.print('成功取关{}个店铺！'.format(len(shop_id_list)))
            else:
                self.print(data)

            await asyncio.sleep(1)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            await self.unsubscribe_goods(session)
            await self.unsubscribe_shops(session)


if __name__ == '__main__':
    run_jd(JdUnsubscribe)
