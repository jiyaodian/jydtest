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
    当存在delete_build文件，且这次push的commit数量为0的时候删除build
    否则继续进行代码规范检测
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

