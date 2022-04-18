#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : jd.py.py
# @Time    : 2022/4/15 3:05 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import multiprocessing
import os
import re
import urllib.parse
import asyncio
from abc import ABCMeta, abstractmethod

from rich.console import Console

from conf.config import JD_CONF
from com.notify import notify


class JdApp(metaclass=ABCMeta):

    def __init__(self, **kwargs):
        self.account = kwargs.get('account', None)
        self.cookie_str = kwargs.get('cookie_str', None)
        self.pt_pin = kwargs.get('pt_pin', None)
        self.pt_key = kwargs.get('pt_key', None)
        self.sort = kwargs.get('sort', None)
        self.conf = kwargs.get('conf')
        self.wq_auth_token = kwargs.get('wq_auth_token', '')
        self._result_msg = None
        self.cookies = {
            'pt_pin': self.pt_pin,
            'pt_key': self.pt_key,
            'wq_auth_token': self.wq_auth_token,
        }
        self.headers = {
            'user-agent': 'jdapp;iPhone;10.4.6;14.1;network/wifi;Mozilla/5.0 (iPhone;'
                          ' CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)'
                          ' Mobile/15E148;supportJDSHWK/1',
            'cookie': self.cookie_str,
        }
        self.console = Console()

    def print(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        style = kwargs.get('style', 'bold red')
        kwargs['style'] = style
        self.console.print(f'账号{self.sort}({self.account})', *args, **kwargs)

    @property
    def result_msg(self):
        """
        任务结果信息
        :return:
        """
        return self._result_msg

    @property
    def help_key(self):
        """
        助力码key
        :return:
        """
        return None

    @abstractmethod
    def app_name(self):
        pass

    @abstractmethod
    async def run(self):
        pass


def run(jd_cls, **kwargs):
    """
    执行京东任务
    :param jd_cls: 活动类
    :param kwargs: 账号相关参数
    :return:
    """
    account = kwargs.get('account', None)
    sort = kwargs.get('sort', '')
    app = jd_cls(**kwargs)
    app_name = app.app_name
    try:
        print(f'账号{sort}({account}):开始执行《{app_name}》...')
        asyncio.run(app.run())
        print(f'账号{sort}({account}):执行完成《{app_name}》...')
        return app.result_msg
    except Exception as e:
        print(f'账号{sort}({account}):执行错误《{app_name}》, 原因:{e.args}')
        return f'执行错误, 原因:{e.args}'


def run_jd(jd_cls):
    """
    京东相关脚本入口
    :param jd_cls:
    :return:
    """
    cookies_list = JD_CONF.get('cookies', None)
    process_num = JD_CONF.get('process_num', 5)

    try:
        JD_CONF.pop('cookies')
        JD_CONF.pop('process_num')
    except:
        pass

    if not cookies_list:
        print('无法运行程序, 配置项:jd.cookies为空...')
        return

    if type(cookies_list) is not list:
        print('无法运行程序, 配置项:jd.cookies类型错误...')
        return

    process_count = os.cpu_count() if os.cpu_count() > process_num else process_num
    process_list = []
    pool = multiprocessing.Pool(process_count)

    notify_title = ''
    for i in range(len(cookies_list)):

        d = {item[0]: item[1] for item in re.findall(r'([^=]+)=([^;]+);?', cookies_list[i] if cookies_list[i] else '')}

        if not d:
            print(f'第{i + 1}个cookies配置错误...')
            del d
            continue
        d['sort'], d['cookie_str'] = i + 1, cookies_list[i]
        d['account'] = d.get('remark', None) if d.get('remark', None) else urllib.parse.unquote(d['pt_pin'])
        d['conf'] = JD_CONF
        process = pool.apply_async(run, args=(jd_cls,), kwds=d)
        process_list.append(process)
        if not notify_title:
            t = jd_cls(**d)
            notify_title = t.app_name

    pool.close()
    pool.join()

    notify_msg = ''
    for process in process_list:
        message = process.get()
        if not message:
            continue
        notify_msg = '\n\n'.join([notify_msg, message])

    notify(notify_title, notify_msg)

