#!/usr/bin/env python
#! coding: utf-8

"""
初始化数据库，添加五千万条数据。每条数据为一个list
"""
from pymongo import Connection

coll = Connection("127.0.0.1", 27017)["test"]["test"]
data = [2934234]*200
for i in xrange(50000000):
	dic = {
		"data": data,
		"uid": i,
	}
	coll.save(dic)



