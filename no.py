#!/usr/bin/env python
#! coding: utf-8

"""
��github��ȡ���ݣ������д�������
������jenkins�������������С���
��Ҫjenkins�Ļ�������
teste
"""
import subprocess
import os
import codecs
import logging
from github import Github

DEBUG = True
PYLINT_MIN_SCORE = 8
