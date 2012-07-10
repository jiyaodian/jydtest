#!/usr/bin/env python
#! coding: utf-8

"""
��github��ȡ���ݣ������д�������
������jenkins�������������С���
��Ҫjenkins�Ļ�������
"""
import subprocess
import os
import codecs
            commit = self.repo.get_commit(i['sha'])
            for j in commit.files:
                if j.filename.endswith('.py'):
                    if j.status == "added" or j.status == 'modified':
                        file_list.append(j.filename)
                    file_list = list(set(file_list))
                    if j.status == 'removed':
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
    ������delete_build�ļ��������push��commit����Ϊ0��ʱ��ɾ��build
    ����������д���淶���
    """
    if os.path.isfile('delete_build'):
        repo = Github('jiyaodian', 'mm6801112').get_user().get_repo('jydtest')
        event = repo.get_events()[0]
        if event.payload['size'] == 0:
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

