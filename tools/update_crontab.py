#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Project : scripts
# @File    : update_crontab.py
# @Time    : 2022/4/18 2:47 PM
# @Author  : ClassmateLin
# @Email   : classmatelin.site@gmail.com
# @Site    : classmatelin.top
# @Cron    : * */12 * * * 
# @Desc    :
import os
import sys
import re


def get_script_list(dir_path=None):
    """
    获取脚本列表
    :return:
    """
    scripts_list = []
    app_dir = os.path.join(dir_path, 'app')

    for d in os.listdir(app_dir):
        abs_d = os.path.join(app_dir, d)
        if os.path.isdir(abs_d) and not d.startswith('_'):
            for file in os.listdir(abs_d):
                abs_file = os.path.join(abs_d, file)
                scripts_list.append(abs_file)
    return scripts_list


def find_cron(script_path):
    """
    查找脚本文件中的cron任务
    :param script_path:
    :return:
    """
    script_filename = os.path.split(script_path)[-1]
    script_name = os.path.splitext(script_filename)[0]
    with open(script_path, 'r') as f:
        text = '\n'.join(f.readlines()[:10])
        search = re.search(r'Cron.*:(.*)', text)
        if not search:
            return None
        cron = search.group(1).strip()

        if cron.startswith('#'):  # 已经关闭的脚本
            return None

        env = "export PYTHONPATH='$PYTHONPATH:/scripts'"
        crontab = r'{} {};python {} >> /scripts/logs/{}_`date "+\%Y-\%m-\%d"`.log 2>&1'. \
            format(cron, env, script_path, script_name)

        comment = re.search(r'@Desc.*:(.*)', text)
        if comment:
            result = '# {}\n{}\n\n'.format(comment.group(1), crontab)
        else:
            result = '{}\n\n'.format(crontab)
        return result


def generate_default_crontab(output='crontab.sh'):
    """
    生成默认的定时任务
    :return:
    """
    pwd = os.path.split(os.path.abspath(sys.argv[0]))[0].replace('tools', '')
    script_list = get_script_list(pwd)

    crontab_headers = [
        '# 默认定时任务\n\n'
        'SHELL=/bin/sh\n\n'
        'PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n\n',
        'MAILTO=root\n\n',
        'HOME=/\n\n',
    ]
    crontab_list = [
        '# 定时更新脚本\n40 4,14,23 * * * /bin/docker-entrypoint >> /dev/null  2>&1\n\n',
    ]

    for script in script_list:

        filepath = os.path.join(pwd, script)
        crontab = find_cron(filepath)
        if not crontab:
            continue
        crontab_list.append(crontab)

    output = os.path.join(pwd, 'shell/{}'.format(output))
    with open(output, 'w+') as f:
        f.writelines(crontab_headers)
        f.writelines(crontab_list)
    print('成功生成crontab任务...')


if __name__ == '__main__':
    generate_default_crontab()

