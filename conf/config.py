#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : config.py
# @Time    : 2022/4/15 2:59 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import json
import os.path
import pathlib
import sys

# 根目录
BASE_DIR = os.path.split(os.path.split(pathlib.Path(__file__).absolute())[0])[0]

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 配置文件路径
CONF_DIR = os.path.join(BASE_DIR, 'conf')  # 项目发布配置文件目录
CONF_PATH = os.path.join(CONF_DIR, 'config.json')   # 项目发布配置文件路径
DEFAULT_CONF_PATH = os.path.join(BASE_DIR, '.config.json')  # 默认配置文件保存路径


try:
    with open(CONF_PATH, encoding='utf-8-sig') as f:   # demo.yaml内容同上例yaml字符串
        cfg = json.load(f)
except FileNotFoundError as e:
    print(f'读取配置文件错误, 找不到文件:{CONF_PATH}')
    sys.exit(0)
except json.decoder.JSONDecodeError as e:
    print(f'读取文件文件错误, JSON文件格式错误:{CONF_PATH}')
    sys.exit(0)


JD_CONF = cfg.get('jd', dict())

# server酱通知token
SERVER_JIANG_TOKEN = cfg.get('notify', dict()).get('server_jiang', None)

# 推送+通知token
PUSH_PLUS_TOKEN = cfg.get('notify', dict()).get('push_plus', None)

# TG机器人Token
TG_BOT_TOKEN = cfg.get('notify', dict()).get('tg', dict()).get('bot_token', None)

# TG用户ID
TG_USER_ID = cfg.get('notify', dict()).get('tg', dict()).get('user_id', None)


# 饿了么配置
ELM_CONF = cfg.get('elm', dict())

# 美团配置
MT_CONF = cfg.get('mt', dict())

XC_CONF = cfg.get('xc', dict())

QDS_CONF = cfg.get('qds', dict())

DSL_CONF = cfg.get('dsl', dict())

IQY_CONF = cfg.get('iqy', dict())
