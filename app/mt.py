#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : mt.py
# @Time    : 2022/4/20 5:33 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import asyncio
import multiprocessing
import os
from abc import ABCMeta, abstractmethod
from rich.console import Console

from com.functions import random_string
from conf.config import MT_CONF


class MtApp(metaclass=ABCMeta):
    
    def __init__(self, **kwargs):
        
        self.token = kwargs.get('token', None)
        self.user_id = kwargs.get('user_id', None)
        
        if not self.token or not self.user_id:
            raise ValueError('token/user_id不能为空...')
        
        self.console = Console()
        
        self.headers = {
            'host': 'game.meituan.com',
            'content-type': 'application/json',
            'mtoken': self.token,
            't': self.token,
            'origin': 'https://mgc.meituan.com',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/15.3.1 meituangroup/com.meituan.imeituan/11.19.205 meituangroup/11.19.205 App/10110/11.19.205 iPhone/iPhone13Pro WKWebView',
            'referer': 'https://mgc.meituan.com/',
        }
        
        self._result_msg = None

        self.device_id = "0000000000000" + random_string(51)
    
    @abstractmethod
    def app_name(self):
        """
        :return: 
        """
        pass
    
    @property
    def result_msg(self):
        return self._result_msg
        
    def print(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        style = kwargs.get('style', 'bold red')
        kwargs['style'] = style
        self.console.print(f'用户({self.user_id}):', *args, **kwargs)
        
    @abstractmethod
    async def run(self):
        pass
    
    
def run(mt_cls, **kwargs):
    """
    执行美团任务
    :param mt_cls: 活动类
    :param kwargs: 账号相关参数
    :return:
    """
    user_id = kwargs.get('user_id', None)
    app = mt_cls(**kwargs)
    app_name = app.app_name
    try:
        print(f'用户({user_id}): 开始执行《{app_name}》...')
        asyncio.run(app.run())
        print(f'用户({user_id}): 执行完成《{app_name}》...')
        return app.result_msg
    except Exception as e:
        print(f'用户({user_id}): 执行错误《{app_name}》, 原因:{e.args}')
        return f'执行错误, 原因:{e.args}'


def run_mt(mt_cls):
    """
    美团相关脚本入口
    :param mt_cls:
    :return:
    """
    users_list = MT_CONF.get('users', None)
    process_num = MT_CONF.get('process_num', 5)

    try:
        MT_CONF.pop('cookies')
        MT_CONF.pop('process_num')
    except:
        pass

    if not users_list:
        print('无法运行程序, 配置项:mt.users为空...')
        return

    if type(users_list) is not list:
        print('无法运行程序, 配置项:mt.users类型错误...')
        return

    process_count = os.cpu_count() if os.cpu_count() > process_num else process_num
    process_list = []
    pool = multiprocessing.Pool(process_count)

    for i in range(len(users_list)):
        kwargs = users_list[i]
        if 'user_id' not in kwargs or 'token' not in kwargs:
            print(f'第{i+1}个用户配置错误, 缺少token或user_id...')
            continue
        kwargs['conf'] = MT_CONF
        process = pool.apply_async(run, args=(mt_cls,), kwds=kwargs)
        process_list.append(process)

    pool.close()
    pool.join()

    for process in process_list:
        message = process.get()
        if not message:
            continue
