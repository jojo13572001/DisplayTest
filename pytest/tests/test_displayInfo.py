from libs.module import Module
import time
import os
import owtClient
import subprocess
import sys
import json

waitTime = 3
#---------------Close All Tested Server and Clients-----------
def close_all_instances():
    os.system('taskkill /f /im chrome.exe')
    os.system('taskkill /f /im DisplaySubprocess.exe')
    os.system('taskkill /f /im DisplayWPF.exe')
    os.system('taskkill /f /im clumsy.exe')
    os.system('taskkill /f /im node.exe')

def check_process(processName, errorMessage):
    progs = str(subprocess.check_output('tasklist'))
    if processName not in progs:
       print(errorMessage)
       close_all_instances()
       sys.exit(0)

def check_state(state, errorMessage):
    if state == False:
       print(errorMessage)
       close_all_instances()
       sys.exit(0)

#Launch p2p servers
def launch_env(currentDir):
    os.system(currentDir+"/../../owt-server-p2p/launch.bat")
    time.sleep(waitTime)
    check_process("node.exe", "Launch owt-server-p2p failure")

#---------------Launch Display-------------------------------
    os.system(currentDir+"/../../DisplayWPF_Net47/launch.bat")
    time.sleep(waitTime)
    check_process("DisplayWPF.exe", "Launch DisplayWPF failure")

#---------------Launch clumsy--------------------------------
    args = '--filter "inbound and ip.SrcAddr == 192.168.1.137"'
    os.system(currentDir+"/../../clumsy/launch.bat " + args)
    time.sleep(waitTime)
    check_process("clumsy.exe", "Launch clumsy failure")

#---------------Launch web client----------------------------
    driver = owtClient.launch(currentDir+"/../../owt-client-javascript/peercall.html", "Entire screen")
    check_process("chrome.exe", "Launch owt-client-javascript failure")
    return driver

def check_state(state, errorMessage):
    if state == False:
       print(errorMessage)
       close_all_instances()
       sys.exit(0)

#---------------Set Environment Variables--------------------
close_all_instances()
os.environ["ControlSignalEndpoint_STAGE"] = "https://localhost:8098"
os.environ["CodeMappingEndpoint_STAGE"] = "https://localhost:8096"
os.environ["SignalingServer"] = "https://localhost:8096"

currentDir = os.path.dirname(os.path.realpath(__file__))

#-------------------Test Cases-------------------------------
def test_check_h264_codec_func():
    driver = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail")
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail")
    owtClient.startShare(driver, "0000")
    result = owtClient.waitStreamReady(driver)
    check_state(result, "wait for stream ready fail")
    strStats = owtClient.getStats(driver)
    while strStats is '':
          strStats = owtClient.getStats(driver)
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           assert Module.check_h264_codec_type(stat['codecId']) is True
    close_all_instances()

def test_check_otp_fail_func():
    driver = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail")
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail")
    owtClient.startShare(driver, "1234")
    assert owtClient.waitforOTPfail(driver) is True
    close_all_instances()

#if vidoe is stopped, we will get the same timestamp from 2 sequential stat reports
def test_check_stopped_func():
    driver = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail")
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail")
    owtClient.startShare(driver, "0000")
    result = owtClient.waitStreamReady(driver)
    check_state(result, "wait for stream ready fail")

    strStats = owtClient.getStats(driver)
    while strStats is '':
          strStats = owtClient.getStats(driver)

    owtClient.stopVideo(driver)
    time.sleep(waitTime)

    strStats = owtClient.getStats(driver)
    assert (strStats == '') is False
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           timeStampStart = stat['timestamp']

    time.sleep(waitTime)
    strStats = owtClient.getStats(driver)
    assert (strStats == '') is False
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           timeStampStop = stat['timestamp']

    assert (timeStampStart == timeStampStop) is True
    close_all_instances()