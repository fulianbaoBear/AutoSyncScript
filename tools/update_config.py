#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/16 3:04 下午
# @File    : update_config.py
# @Project : jd_scripts
# @Desc    :
import os
import shutil
import sys
import json
from conf.config import CONF_PATH, DEFAULT_CONF_PATH


def read_json(file):
    """
    读取json文件内容
    :param file:
    :return:
    """
    with open(file, encoding='utf-8-sig') as f:   # demo.yaml内容同上例yaml字符串
        data = json.load(f)
        return data

# func mergeConfig(publishedConfig map[string]interface{}, defaultConfig map[string]interface{}) map[string]interface{} {
# 	for key, val := range defaultConfig {
# 		if reflect.TypeOf(val) == reflect.TypeOf(map[string]interface{}{}) {
# 			m, ok := publishedConfig[key]
# 			if !ok {
# 				publishedConfig[key] = val
# 			} else {
# 				val = mergeConfig(m.(map[string]interface{}), val.(map[string]interface{}))
# 				publishedConfig[key] = val
# 			}
# 			continue
# 		}
# 		_, ok := publishedConfig[key]
# 		if ok {
# 			continue
# 		} else {
# 			publishedConfig[key] = val
# 		}
# 	}
# 	return publishedConfig
# }


def merge_json(p_conf, d_conf):
    """
    已发布配置
    :param p_conf:
    :param d_conf:
    :return:
    """
    for key, val in d_conf.items():
        if type(val) == dict:
            if key not in p_conf:
                p_conf[key] = val
            else:
                p_conf[key] = merge_json(p_conf[key], d_conf[key])

        if key not in p_conf:
            p_conf[key] = val
    return p_conf


def update_config():
    """
    更新配置文件
    :return:
    """
    published_conf = read_json(CONF_PATH)
    default_conf = read_json(DEFAULT_CONF_PATH)
    res = merge_json(published_conf, default_conf)
    with open(CONF_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(res, f, indent=4, sort_keys=True)
    print(f'成功更新配置文件至:{CONF_PATH}')


if __name__ == '__main__':
    update_config()
