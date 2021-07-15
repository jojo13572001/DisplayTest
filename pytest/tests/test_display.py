from libs.module import Module
import time
import os
import owtClient
import subprocess
import sys
import json
import grpc
currentDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDir+'/../../proto/generated')
import owt_server_p2p_pb2, owt_server_p2p_pb2_grpc
import display_pb2, display_pb2_grpc
import clumsy_pb2, clumsy_pb2_grpc

waitTime = 3
owt_server_p2p_Address = 'localhost:50051'
displayAddress = 'localhost:50052'
clumsyAddress = 'localhost:50053'

ControlSignalEndpoint_STAGE="https://localhost:8098"
CodeMappingEndpoint_STAGE="https://localhost:8096"
SignalingServer="https://localhost:8096"

#---------------Close All Tested Server and Clients-----------
def close_all_instances(owt_server_p2pStub, displayStub, clumsyStub):
    os.system('taskkill /f /im chrome.exe')
    if displayStub != None:
       displayStub.Terminate(display_pb2.TerminateRequest(processName="DisplayWPF.exe",
                                                          subProcessName="DisplaySubprocess.exe"))
    if clumsyStub != None:
       clumsyStub.Terminate(clumsy_pb2.TerminateRequest(processName="clumsy.exe"))
    if owt_server_p2pStub != None:
       owt_server_p2pStub.Terminate(owt_server_p2p_pb2.TerminateRequest(processName="node.exe"))

def check_process(processName, errorMessage, owt_server_p2pStub, displayStub, clumsyStub):
    progs = str(subprocess.check_output('tasklist'))
    if processName not in progs:
       print(errorMessage)
       close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)
       sys.exit(0)

def check_state(state, errorMessage, owt_server_p2pStub, displayStub, clumsyStub):
    if state == False:
       print(errorMessage)
       close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)
       sys.exit(0)

#Launch p2p servers
def launch_env(currentDir):
#---------------Remote Launch owt-server-p2p-------------------------------
    channel = grpc.insecure_channel(owt_server_p2p_Address)
    owt_server_p2pStub = owt_server_p2p_pb2_grpc.LaunchStub(channel)
    response = owt_server_p2pStub.Start(owt_server_p2p_pb2.LaunchRequest(processName="node.exe"))
    check_state(response.result=="OK", response.message, owt_server_p2pStub, None, None)

#---------------Remote Launch Display-------------------------------
    channel = grpc.insecure_channel(displayAddress)
    displayStub = display_pb2_grpc.LaunchStub(channel)
    response = displayStub.Start(display_pb2.LaunchRequest(ControlSignalEndpoint_STAGE=ControlSignalEndpoint_STAGE,
                                                           CodeMappingEndpoint_STAGE=CodeMappingEndpoint_STAGE,
                                                           SignalingServer=SignalingServer,
                                                           processName="DisplayWPF.exe"))
    check_state(response.result=="OK", response.message, owt_server_p2pStub, displayStub, None)

#---------------Remote Launch clumsy--------------------------------
    channel = grpc.insecure_channel(clumsyAddress)
    clumsyStub = clumsy_pb2_grpc.LaunchStub(channel)
    response = clumsyStub.Start(clumsy_pb2.LaunchRequest(args='--filter "inbound and ip.SrcAddr == 192.168.1.137"', 
                                                         processName="clumsy.exe"))
    check_state(response.result=="OK", response.message, owt_server_p2pStub, displayStub, clumsyStub)

#---------------Local Launch web client----------------------------
    driver = owtClient.launch(currentDir+"/../../owt-client-javascript/peercall.html", "Entire screen")
    check_process("chrome.exe", "Launch owt-client-javascript failure", owt_server_p2pStub, displayStub, clumsyStub)
    return driver, owt_server_p2pStub, displayStub, clumsyStub

#-------------------Test Cases-------------------------------------
def test_check_h264_codec_func():
    driver, owt_server_p2pStub, displayStub, clumsyStub = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    owtClient.startShare(driver, "0000")
    result = owtClient.waitStreamReady(driver)
    check_state(result, "wait for stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    strStats = owtClient.getStats(driver)
    while strStats == '':
          strStats = owtClient.getStats(driver)
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           assert Module.check_h264_codec_type(stat['codecId']) is True
    close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)

def test_check_otp_fail_func():
    driver, owt_server_p2pStub, displayStub, clumsyStub = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    owtClient.startShare(driver, "1234")
    assert owtClient.waitforOTPfail(driver) is True
    close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)

#if vidoe is stopped, we will get the same timestamp from 2 sequential stat reports
def test_check_stopped_func():
    driver, owt_server_p2pStub, displayStub, clumsyStub = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    owtClient.startShare(driver, "0000")
    result = owtClient.waitStreamReady(driver)
    check_state(result, "wait for stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)

    strStats = owtClient.getStats(driver)
    while strStats == '':
          strStats = owtClient.getStats(driver)

    owtClient.stopVideo(driver)
    time.sleep(waitTime)

    strStats = owtClient.getStats(driver)
    assert (strStats == '') is False
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           timeStampStart = stat['timestamp']

    strStats = owtClient.getStats(driver)
    assert (strStats == '') is False
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           timeStampStop = stat['timestamp']

    assert (timeStampStart == timeStampStop) is True
    close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)