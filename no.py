#!/usr/bin/env python
#! coding: utf-8

"""
从github获取数据，并进行代码风格检查
必须在jenkins服务器上面运行。。
需要jenkins的环境变量
teste
"""
import subprocess
import os
import codecs
import logging
from github import Github

DEBUG = True
PYLINT_MIN_SCORE = 8
