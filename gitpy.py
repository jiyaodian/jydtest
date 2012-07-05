#!/usr/bin/env python
#! coding: utf-8

"""
isdfsdf
"""

import sys
import os
import subprocess

def git(args, **kwargs):
    environ = os.environ.copy()
    if 'repo' in kwargs:
        environ['GIT_DIR'] = kwargs['repo']
    if 'work' in kwargs:
        environ['GIT_WORK_TREE'] = kwargs['work']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, env=environ)
    return proc.communicate()

def get_changed_files(base, commit, **kw):
    (results, code) = git(('git', 'diff', '--numstat', "%s..%s" % (base, commit)), **kw)
    lines = results.split('\n')[:-1]
    return map(lambda x: x.split('\t')[2], lines)

def get_new_file(filename, commit):
    (results, code) = git(('git', 'show', '%s:%s' % (commit, filename)))
    return results

repo = os.getcwd()
basedir = os.path.join(repo, "..")

line = sys.stdin.read()
(base, commit, ref) = line.strip().split()
modified = get_changed_files(base, commit)

for fname in modified:
    print "=====", fname
    print get_new_file(fname, commit)
