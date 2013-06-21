#!/usr/bin/env python
#! coding: utf-8

import time
from pymongo import Connection

conn = Connection("127.0.0.1", 27017)
coll = conn["test"]["test"]

start_time = time.time()


for i in xrange(100000):
	coll.find_one({"uid":i})

end_time = time.time()
cost_time = end_time - start_time
print("cost time %s, %ss/1w"%(cost_time, cost_time/10000))



