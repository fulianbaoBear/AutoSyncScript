#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : notify.py
# @Time    : 2022/4/15 2:54 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    : 消息通知
import json

import requests

from conf.config import TG_BOT_TOKEN, TG_USER_ID, SERVER_JIANG_TOKEN


def telegram_notify(title, body):
    """
    :param title:
    :param body:
    :return:
    """
    if not TG_USER_ID or TG_BOT_TOKEN:
        print('未配置TG_USER_ID/TG_BOT_TOKEN, 无法发送Telegram通知...')
        return

    url = "https://api.telegram.org/bot{}/sendMessage".format(TG_BOT_TOKEN)
    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
    }
    body = {
        "chat_id": TG_USER_ID,
        "text": '\n\n'.join([title, body])
    }

    try:
        response = requests.post(url=url, headers=headers, data=body)
        data = response.json()
        if data.get('ok'):
            print('成功发送Telegram通知...')
        else:
            print('无法发送Telegram通知, 响应正文:{}'.format(json.dumps(body)))
    except Exception as e:
        print(f'TG通知异常:{e.args}')


def server_jiang_notify(title, body):
    """
    server酱通知
    :param title:
    :param body:
    :return:
    """

    if not SERVER_JIANG_TOKEN:
        print('未配置SERVER_JIANG_TOKEN, 无法发送Server酱通知...')
        return

    url = "https://sc.ftqq.com/{}.send".format(SERVER_JIANG_TOKEN)

    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
    }

    body = {
        "text": title,
        "desp": body,
    }

    try:
        response = requests.post(url=url, headers=headers, data=body)
        data = response.json()
        if data.get('code', -1) == 0:
            print('成功发送server酱通知...')
        else:
            print('无法发送server酱通知, 响应正文:{}'.join(json.dumps(body)))
    except Exception as e:
        print(f'发送server酱通知异常:{e.args}')


def notify(title, body):
    """
    :param title:
    :param body:
    :return:
    """
    telegram_notify(title, body)

    server_jiang_notify(title, body)
