#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/10 上午9:49
# @Author  : chenyuelong
# @Mail    : yuelong_chen@yahoo.com
# @File    : ppmonitor.py
# @Software: PyCharm

import os, sys
import argparse
from utils import getArgs,pipeline



def main():
    args = getArgs()
    pipeline(args.mainPid,os.path.abspath(args.out),
             os.path.abspath(args.tmp),os.path.abspath(args.log))


if __name__ == '__main__':
    main()