#!/usr/bin/env python
#! coding: utf-8

"""
从github获取数据，并进行代码风格检查
必须在jenkins服务器上面运行。。
需要jenkins的环境变量
"""
import subprocess
import os
import codecs
import logging
from github import Github
sdfsfs
sf
sss
sdos
sos
fa

DEBUG = True
PYLINT_MIN_SCORE = 8

def init_log():
    """
    init logger
    """
    logger = logging.getLogger("style_check")
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler('style_check.log')
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

class StyleCheck:
    """
    运行test进行测试
    """
    def __init__(self, repo_name, git_user, git_pwd):
        """
        初始化工作，没有考虑异常
        """
        self.repo = Github(git_user, git_pwd).get_user().get_repo(repo_name)
        self.event = self.repo.get_events()[0]
        if self.event.payload['size'] == 0:
            return
        tmp = self.event.payload['commits'][0]['sha']
        self.before_sha = self.repo.get_commit(tmp).parents[0].sha

        self.logger = init_log()

    def run_command(self, args, cwd="."):
        """
        运行命令
        """
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, \
                stderr=subprocess.PIPE, cwd=cwd)
        print ' '.join(args)
        self.logger.info(' '.join(args))
        return proc.communicate()

    def git_reset(self):
        """
        hard-reset
        """
        (results, code) = self.run_command(('git', 'reset', '--hard', \
                self.before_sha))
        if DEBUG: 
            print code
            print results
        (results, code) = self.run_command(('git', 'push', '--force'))
        if DEBUG: 
            print code
            print results

    def single_style_check(self, code_path):
        """
        检查代码风格，返回检查结果和分数
        """
        try:
            (results, code) = self.run_command(('pylint', '-f', 'parseable', 
                code_path))
        except Exception:
            print 'run pylint error'
            return ("", 0)
        if DEBUG:
            print "error info", code
        try:
            score = float([r for r in results.split('\n') if
                    r.startswith('Your code')][0].split(' ')[6].split('/')[0])
        except Exception:
            score = None
        return (results, score)

    def test(self):
        """
        test
        """
        if self.event.payload['size'] == 0: #没有commit,直接返回，不用进行代码检测
            return 2

        pylint_log = codecs.open('pylint.log', 'w', 'utf-8')
        style_pass = True
        file_list = self.get_file_list()

        for file_path in file_list:
            (detail, score) = self.single_style_check(file_path)
            if score is not None:
                if score < PYLINT_MIN_SCORE:
                    style_pass = False
                    print detail
                pylint_log.writelines(detail)
            else:
                print 'score is None'
        pylint_log.close()

        if style_pass is False:
            self.git_reset()
            tmp_f = open('delete_build', 'w')
            tmp_f.write(os.environ['BUILD_NUMBER'])
            tmp_f.close()
            return 1
        return 0

    def get_file_list(self):
        """
        从payload字典中获取commits的sha，在通过sha获取commit，
        然后从commit里面得到修改的文件
        只检查.py文件
        """
        file_list = []
        #ignore_list = []
        for i in self.event.payload['commits']:
            commit = self.repo.get_commit(i['sha'])
            for j in commit.files:
                if DEBUG:
                    print j.filename, j.status
                if j.filename.endswith('.py'):
                    if j.status == "added" or j.status == 'modified':
                        file_list.append(j.filename)
                    file_list = list(set(file_list))
                    if j.status == 'removed':
                        file_list.remove(j.filename)
        return file_list

def delete_build():
    """
    删除jenkins 正在运行的构建
    java -jar /home/jiyd/.jenkins/war/WEB-INF/jenkins-cli.jar -s 
    http://app.maimiaotech.com:8787 delete-builds test $BUILD_NUMBER
    """
    proc = subprocess.Popen(('java', '-jar', \
            os.environ['JENKINS_HOME']+'/war/WEB-INF/jenkins-cli.jar',\
            '-s', 'http://app.maimiaotech.com:8787', 'delete-builds',\
            'test', os.environ['BUILD_NUMBER']), \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (results, code) = proc.communicate()
    if DEBUG:
        print code
        print results

def main():
    """
    常量信息最好通过配置文件输入
    当存在delete_build文件，且这次push的commit数量为0的时候删除build。
    否则继续进行代码规范检测
    """
    if os.path.isfile('delete_build'):
        repo = Github('jiyaodian', 'mm6801112').get_user().get_repo('jydtest')
        event = repo.get_events()[0]
        if event.payload['size'] == 0:
            print 'delete build'
            #delete_build()
        os.remove('delete_build')
        code = 0
    else:
        style_check = StyleCheck('jydtest', 'jiyaodian', 'mm6801112')
        code = style_check.test()
    return code

if __name__ == '__main__':
    if main() == 1:
        exit(1)
        sd

