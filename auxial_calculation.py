#!/usr/bin/python3.6
# -- coding: utf-8 --
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
汎用外部計算機実行スクリプト
* 処理順序
  + 入力パラメータ転送
  + 事前処理
  + 本番処理
  + 事後処理
  + 圧縮アーカイブ
  + アーカイブ転送
  + アーカイブ解凍
'''
import os
import sys
import time
import glob
import shutil
import datetime
import subprocess

#BASE_DIR = os.path.split(os.path.dirname(__file__))[0:-1]
BASE_DIR = os.path.dirname(__file__)
print("BASE_DIR = %s"%BASE_DIR)
sys.path.append(BASE_DIR)
if ("REMOTE_HOSTNAME" in os.environ) is True:
    REMOTE_HOSTNAME = os.environ["REMOTE_HOSTNAME"]
else:
    sys.stderr.write("環境変数'REMOTE_HOSTNAME'が設定されていません。\n")
    sys.stderr.flush()
    sys.exit(1)

CALCDIR = None

def error_log(messages):
    '''
    エラー/ワーニング出力→標準エラー出力
    '''

    sys.stderr.write("%s:%s\n"%(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), messages))
    sys.stderr.flush()

def info_log(messages):
    '''
    メッセージ出力→標準出力
    '''

    sys.stdout.write("%s:%s\n"%(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), messages))
    sys.stdout.flush()

def preProcess():
    '''
    事前処理
    '''

    global CALCDIR

    #if os.path.exists("pre_process.sh") is False:
    #    error_log("事前処理用のスクリプトがありません。")
    #    return False

    info_log("事前処理を実行します。")
    #os.chdir("../")
    cmd = 'ssh %s "cd ~/remote_calculation/%s; bash pre_process.sh"'%(REMOTE_HOSTNAME, CALCDIR)
    print(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc.wait()
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:

        print("事前処理が異常終了しました")
        print(stdout.decode("UTF-8"))
        print(stderr.decode("UTF-8"))

        return False

def postProcess():
    '''
    事後処理
    '''

    global CALCDIR

    #if os.path.exists("post_process.sh") is False:
    #    error_log("事前処理用のスクリプトがありません。")
    #    return False

    info_log("事後処理を実行します。")
    #os.chdir("../")
    cmd = 'ssh %s "cd ~/remote_calculation/%s; bash post_process.sh"'%(REMOTE_HOSTNAME, CALCDIR)
    print(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc.wait()
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:

        print("事後処理が異常終了しました")
        print(stdout.decode("UTF-8"))
        print(stderr.decode("UTF-8"))

        return False

def qsubProcess():
    '''
    本実行
    ../resourcesディレクトリにqsubスクリプト「qsub_process.sh」を配置しておく。
    本館数では、qsubスクリプト実行後、終了待ち合わせを行う
    '''

    global CALCDIR

    # 計算ジョブの投入
    #os.chdir(current_dir)
    info_log("計算ジョブを投入します。")
    cmd = 'ssh nims-spacom "cd ~/remote_calculation/%s; qsub2 qsub_process.sh"'%CALCDIR

    info_log(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc.wait()
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:

        error_log("計算ジョブの投入に失敗しました")
        error_log(stdout.decode("UTF-8"))
        error_log(stderr.decode("UTF-8"))

        #sys.exit(1)
        return False

    # 計算終了待ち合わせ
    jobid = stdout.decode("UTF-8").split("\n")[-1]
    if jobid == "":
        jobid = stdout.decode("UTF-8").split("\n")[-2]
    if jobid == "":
        error_log("JOB IDが取得できませんでした。")
        count = 0
        for item in stdout.decode("UTF-8").split("\n"):
            info_log("[%03d]:%s"%(count, item))
            count += 1
    #        sys.exit(1)
            return False

    info_log("JOB ID(%s)でジョブ開始を確認"%jobid)

    qstat_cmd = "ssh nims-spacom qstat -x %s"%jobid
    while True:
        # 10秒間隔で終了を検査
        proc = subprocess.Popen(qstat_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            error_log("計算ジョブのステータス取得に失敗しました。")
            error_log(stdout.decode("UTF-8"))
            error_log(stderr.decode("UTF-8"))
        #    sys.exit(1)
            return False

        status = stdout.decode("utf-8").split("\n")[2].split()[4]

        if status == "C" or status == "F":
            info_log("計算ジョブが終了しました（status = %s)"%status)
            break
        elif status == "E":
            error_log("計算ジョブがエラー終了しました（status = %s)"%status)
        #    sys.exit(1)
            return False
        #elif status == "F":
        #    error_log("計算ジョブが異常終了しました（status = %s)"%status)
        #    sys.exit(1)
        #    return False
        time.sleep(10.0)

    return True

def main():
    '''
    開始点
    '''

    global CALCDIR
    isPreProcess = isPostProcess = False
    current_dir = os.getcwd()
    CALCDIR = os.path.basename(current_dir)

    # 事前処理
    #../resourcesディレクトリにpre_process.shファイルがあれば
    #preProcess関数でそれを読み込み、事前スクリプトとして実行する
    #※ qsub実行はできるが、終了待ち合わせはpre_process.shで実施すること。
    if os.path.exists("%s/resources/pre_process.sh"%BASE_DIR) is True:
        #shutil.copyfile("%s/resources/pre_process.sh"%BASE_DIR, "./pre_process.sh")
        info_log("事前処理が予約されました。")
        isPreProcess = True
    # 事後処理
    #../resourcesディレクトリにpost_process.shファイルがあれば
    #postProcess関数でそれを読み込み、事前スクリプトとして実行する
    #※ qsub実行はできるが、終了待ち合わせはpre_process.shで実施すること。
    if os.path.exists("%s/resources/post_process.sh"%BASE_DIR) is True:
        #shutil.copyfile("%s/resources/post_process.sh"%BASE_DIR, "./post_process.sh")
        info_log("事後処理が予約されました。")
        isPostProcess = True
    # qsubスクリプト
    if os.path.exists("%s/resources/qsub_process.sh"%BASE_DIR) is True:
        shutil.copyfile("%s/resources/qsub_process.sh"%BASE_DIR, "./qsub_process.sh")
    else:
        error_log("qsubプロセススクリプトファイルがありませんでした。")
        sys.exit(1)

    # 事前処理または事後処理どちらかを実行する場合に、resources以下のファイルをコピーする（付属スクリプトなどのため）
    if isPreProcess is True or isPostProcess is True:
        #shutil.copyfile("%s/resources/*"%BASE_DIR, "./")
        info_log("事前、事後処理用のファイルを準備します。")
        cmd = "cp -rp %s/resources/* ./"%BASE_DIR
        #copyfiles = glob.glob("%s/resources/*"%BASE_DIR)
        #for item in copyfiles:
        #    shutil.copy(item, "./")
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        proc.wait()
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:

            print("計算ディレクトリの準備に失敗しました")
            print(stdout.decode("UTF-8"))
            print(stderr.decode("UTF-8"))
    
            sys.exit(1)

    # データを転送
    info_log("データを転送します。")
    os.chdir("../")                         # ~/remote_calculationへ移動
    cmd = "scp -rp ./%s/ nims-spacom:~/remote_calculation/%s/"%(CALCDIR, CALCDIR)
    print(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc.wait()
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:

        print("計算ディレクトリの投入に失敗しました")
        print(stdout.decode("UTF-8"))
        print(stderr.decode("UTF-8"))

        sys.exit(1)

    # 事前処理
    if isPreProcess is True:
        info_log("事前処理を実行します。")
        ret = preProcess()
        if ret is False:
            error_log("事前処理が異常終了しました。")
            sys.exit(1)
    # qsub実行
    ret = qsubProcess()
    if ret is False:
        error_log("計算処理が異常終了しました。")
        sys.exit(1)

    # 事後処理
    if isPostProcess is True:
        info_log("事後処理を実行します。")
        ret = postProcess()
        if ret is False:
            error_log("事後処理が異常終了しました。")
            sys.exit(1)

    # 計算結果の取り込み
    info_log("計算ディレクトリ内容を転送します。")
    os.chdir(current_dir)                         # ~/remote_calculation/計算ディレクトリへ移動
    cmd = "scp -rp nims-spacom:~/remote_calculation/%s/* ./"%CALCDIR
    info_log(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc.wait()
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:

        error_log("計算ディレクトリの転送に失敗しました")
        error_log(stdout.decode("UTF-8"))
        error_log(stderr.decode("UTF-8"))

        sys.exit(1)

# 開始点
if __name__ == "__main__":

    #execute_fister_dpf()
    main()

