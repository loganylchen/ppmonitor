#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/10 上午9:47
# @Author  : chenyuelong
# @Mail    : yuelong_chen@yahoo.com
# @File    : utils.py
# @Software: PyCharm

import time
# import os, sys
import subprocess
import argparse
import random
import string
import re
import pandas as pd
# import numpy as np
import matplotlib

matplotlib.use('Agg')
# import matplotlib.pyplot as plt
import seaborn as sns


def getArgs():
    '''
    命令行参数获得，目前版本只针对shell脚本，并对shell脚本中的每一行命令进行统计
    :return: args
    '''
    parser = argparse.ArgumentParser(prog='ppmonitor',
                                     description='shell脚本监控程序，监控shell脚本中每一行命令所用内存及cpu统计')
    # parser.add_argument('-sh', '--shell', dest='shellScript', type=str, required=True, action='store',
    #                     help='shell脚本，e.g. test.sh')
    parser.add_argument('-pid', '--pid', dest='mainPid', type=str, required=True, action='store',
                        help='需要监控的进程号，程序会监控该进程号及其子进程')
    parser.add_argument('-o', '--out', dest='out', type=str, required=True, action='store',
                        help='输出目录prefix')
    parser.add_argument('-t', '--tmp', dest='tmp', type=str, action='store',
                        help='tmp目录，e.g. /tmp/', default='/tmp/')
    parser.add_argument('-log', '--log', dest='log', type=str, action='store',
                        help='log，e.g. test.sh.log', default='')
    args = parser.parse_args()
    return args


def Popen(cmd):
    '''
    subprocess包装
    :param cmd: 需要运行的命令
    :return: popen
    '''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return p


def randomFileName(cache):
    '''
    生成随机20位长度的文件名，例如：KG9skf8s9fd0s0dfg.tmp
    :param cache: 所有生成的文件名都需要记录，最终进行统计及删除
    :return:文件名
    '''
    rf = '{}.tmp'.format(''.join(random.sample(string.ascii_letters + string.digits, 20)))
    cache[rf] = 1
    return rf, cache


def getpids(pid):
    '''
    由于有的程序会调用多进程，或者程序间的调用，会形成不同的子进程。这是一个利用pstree查找
    所有该进程相关子进程的方法
    :param pid: pid 父进程pid
    :return: pidlist 父进程及父进程所有子进程 pid
    '''
    p = Popen(getchildPidCmd(pid))
    stdout, _ = p.communicate()
    pidstr = stdout.decode('utf-8')
    pidlist = pattern4pid(pidstr)
    return pidlist


def pattern4pid(pidstr):
    '''
    通过pstree返回值，利用正则表达式找出所有pid
    :param pidstr:pstree返回结果
    :return: pidlist
    '''
    pattern = re.compile('\(([\d]+)\)')
    pidlist = pattern.findall(pidstr)
    return pidlist


def getchildPidCmd(pid):
    '''
    pstree cmd
    :param pid:
    :return: cmd
    '''
    cmd = 'pstree -p {}'.format(pid)
    return cmd


def getstatCmd(pid):
    '''
    生成pidstat命令
    :param pid: pid
    :return: cmd
    '''
    cmd = 'pidstat -urd -h -p {} 1 1'.format(pid)
    return cmd


def plotResult(file, outdir):
    '''
    以统计文件及图的形式输出结果
    :param file: pidstat统计结果文件（完成后会进行删除）
    :param outdir: 统计结果输出目录
    :return: 无
    '''
    data = pd.read_table(file, sep='\s+', skip_blank_lines=True, comment='#')
    data.columns = ['Time', 'UID', 'PID', 'pusr', 'psystem', 'pguest', 'pCPU', 'CPU', 'minflt/s',
                    'majflt/s', 'VSZ', 'RSS', '%MEM', 'kB_rd/s', 'kB_wr/s', 'kB_ccwr/s', 'Command']
    data['Time'] = data['Time'] - min(data['Time'])
    data['VSZ'] = data['VSZ'] / 1000000
    data['RSS'] = data['RSS'] / 1000000
    data.groupby('Command').describe().to_csv('{}.summary.csv'.format(outdir))
    # print(data)
    sns_plot = sns.pairplot(data, x_vars=["RSS", "VSZ"], y_vars=['Time'],
                            hue='Command', size=10)
    sns_plot.savefig("{}.Time_VSZ_RSS.pdf".format(outdir), dpi=300)
    p = Popen('rm {}'.format(file))
    _, _ = p.communicate()



def pipeline(pid, outdir, tmp, log):
    '''
    流程
    :param shs:脚本
    :param outdir: 输出路径
    :param tmp: tmp路径
    :param log: 暂时未使用
    :return: 无
    '''
    cache = {}
    # cmd = 'sh {}'.format(shs)
    # fp = Popen(cmd)
    fatherPid = pid
    file = pidstat(fatherPid, cache, tmp)
    plotResult(file, outdir)
    # _, _ = fp.communicate()
    print('Finish!!!')


def pidstat(pid, cache, tmp='/tmp/'):
    '''
    pidstat进行进程统计，并将结果输出到tmp目录中
    :param pid: pid
    :param cache: 文件名dict
    :param tmp: tmp目录
    :return: file
    '''
    rf, cache = randomFileName(cache)
    # cmd = getstatCmd(pid)
    file = '{}/{}'.format(tmp, rf)

    pidlist = getpids(pid)

    while (len(pidlist) > 0):
        for cpid in pidlist:
            cmd = getstatCmd(cpid)
            p = Popen(cmd)
            stdout, _ = p.communicate()
            with open(file, 'a+') as f:
                f.write('#stdout:{}'.format(stdout.decode('utf-8')))

        pidlist = getpids(pid)
        time.sleep(10)  # 统计时间一般10秒一次
        # p = Popen(cmd)
        # stdout, stderr = p.communicate()
        # print('stdout:{}'.format(stdout.decode('utf-8')))
    return file


def main():
    # getArgs()
    cache = {}
    # print(randomFileName(cache))
    pidstat(29709, cache, '/home/chenyl/TMPS/')
    # getpids(27742)


if __name__ == '__main__':
    main()
