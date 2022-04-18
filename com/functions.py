#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : functions.py
# @Time    : 2022/4/18 11:13 AM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import math
import random


def random_integer_string(n=16):
    """
    生成整形字符串
    :param n:
    :return:
    """
    t = "0123456789"
    s = ''

    while len(s) < n:
        s += t[random.randint(0, len(t) - 1)]

    return s


def random_string(e=40):
    """
    生成随机字符串
    :param e:
    :return:
    """
    t = "abcdefhijkmnprstwxyz123456789"
    len_ = len(t)
    s = ""
    for i in range(e):
        s += t[math.floor(random.random() * len_)]
    return s
