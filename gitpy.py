#!/usr/bin/env python
#! coding: utf-8

"""
��github��ȡ���ݣ������д�������
������jenkins�������������С���
��Ҫjenkins�Ļ�������
�����趨��� ȫ�ֱ���
sfd
"""
import subprocess
import os
import sys
import codecs
import logging
from github import Github

DEBUG = True
REPO_HOME = '/home/jiyd/repo'
PYLINT_MIN_SCORE = 8
GUSER = 'jiyaodian'
GPWD = 'mm6801112'
GREPONAME = 'jydtest'

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
    ����test���в���
    """
    def __init__(self, repo_name, local_repo_home, git_user, git_pwd):
        """
        ��ʼ��������û�п����쳣
        ���event.payload['size']Ϊ0��ֱ�ӷ���
        """
        self.repo = Github(git_user, git_pwd).get_user().get_repo(repo_name)
        self.event = self.repo.get_events()[0]
        if self.event.payload['size'] == 0:
            return
        tmp = self.event.payload['commits'][0]['sha']
        self.before_sha = self.repo.get_commit(tmp).parents[0].sha
        self.git_url = u'git@github.com:'+self.repo.full_name+u'.git'
        self.local_repo_home = local_repo_home
        self.repo_dir = local_repo_home + '/'+repo_name+'/'

        self.logger = init_log()

    def run_command(self, args, cwd=os.environ['WORKSPACE']):
        """
        ��������
        """
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, \
                    stderr=subprocess.PIPE, cwd=cwd)
        except OSError:
            self.logger.error(str(sys.exc_info()))
        if DEBUG:
            print ' '.join(args)
        self.logger.info(' '.join(args))
        return proc.communicate()

    def git_clone(self):
        """
        git clone
        """
        (results, code) = self.run_command(('git', 'clone', self.git_url), \
                cwd=self.local_repo_home)
        if DEBUG:
            print code
            print results

    def git_pull(self):
        """
        pull the newest data
        """
        (results, code) = self.run_command(('git', 'pull'), self.repo_dir)
        if DEBUG:
            print code
            print results

    def git_reset(self):
        """
        hard-reset
        """
        (results, code) = self.run_command(('git', 'reset', '--hard', \
                self.before_sha), self.repo_dir)
        if DEBUG:
            print code
            print results
        (results, code) = self.run_command(('git', 'push', '--force'), \
                self.repo_dir)
        if DEBUG:
            print code
            print results

    def single_style_check(self, code_path):
        """
        �������񣬷��ؼ�����ͷ���
        """
        try:
            (results, code) = self.run_command(('pylint', '-f', 'parseable', 
                code_path), self.repo_dir)
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
        ���д�����
        ���event����commit����Ϊ0������event����PushEent���ͣ�ֱ�ӷ���
        """
        if self.event.payload['size'] == 0 or self.event.type != 'PushEvent': #û��commit,ֱ�ӷ��أ����ý��д�����
            return 2
        if not os.path.exists(self.repo_dir):
            self.git_clone()
        else:
            self.git_pull()

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

    def get_ignore_list(self):
        """
        �������ļ��ж�ȡ�����д�������ļ��б�
        �����ļ�����
        ÿ��һ�����·��
        ��.py��β������Ϊ���ļ� ------> ͨ��file_name in ignore_list �ж�
        ������Ϊ���ļ���-----> startswith �����ж�
        return: (�ļ������б�, �ļ����б�)
        """
        pass

    def get_file_list(self):
        """
        ��payload�ֵ��л�ȡcommits��sha����ͨ��sha��ȡcommit��
        Ȼ���commit����õ��޸ĵ��ļ�
        ֻ���.py�ļ�
        """
        file_list = []
        #ignore_list = []
        for i in self.event.payload['commits']:
            commit = self.repo.get_commit(i['sha'])
            for j in commit.files:
                if DEBUG:
                    print i['sha'], j.filename, j.status
                if j.filename.endswith('.py'):
                    if j.status == "added" or j.status == 'modified':
                        file_list.append(j.filename)
                    file_list = list(set(file_list))
                    if j.status == 'removed' and j.filename in file_list:
                        file_list.remove(j.filename)
        return file_list

def delete_build():
    """
    ɾ��jenkins �������еĹ���
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
    ������Ϣ���ͨ�������ļ�����
    ������delete_build�ļ��������push��commit����Ϊ0��ʱ��ɾ��build��
    ����������д���淶���
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
        style_check = StyleCheck('jydtest', REPO_HOME, 'jiyaodian', 'mm6801112')
        code = style_check.test()
    return code

if __name__ == '__main__':
    if main() == 1:
        exit(1)


