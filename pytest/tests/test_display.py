from libs.module import Module
import time
import os
from pathlib import Path
import owtClient
import subprocess
import sys
import json
import grpc
import configparser
currentDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDir+'/../../proto/generated')
import owt_server_p2p_pb2, owt_server_p2p_pb2_grpc
import display_pb2, display_pb2_grpc
import clumsy_pb2, clumsy_pb2_grpc

config = configparser.ConfigParser()
config.read(currentDir + "/../../config.ini")

waitTime = 5

owt_server_p2p_rpc_Address = config['SignalingServer']['IP'] + ":"+ config['SignalingServer']['RPC_PORT']

display_rpc_Address = config['Display']['IP'] + ":" + config['Display']['RPC_PORT']
clumsy_rpc_Address = config['Clumsy']['IP'] + ":" + config['Clumsy']['RPC_PORT']

ControlSignalEndpoint_STAGE = "https://" + config['ControlSignalEndpoint_STAGE']['IP'] + ":" + config['ControlSignalEndpoint_STAGE']['PORT']
CodeMappingEndpoint_STAGE = "https://" + config['CodeMappingEndpoint_STAGE']['IP'] + ":" + config['CodeMappingEndpoint_STAGE']['PORT']
SignalingServer = "https://" + config['SignalingServer']['IP'] + ":" + config['SignalingServer']['PORT']

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
       #sys.exit(0)

#Launch p2p servers
def launch_env(currentDir):
#---------------Remote Launch owt-server-p2p-------------------------------
    channel = grpc.insecure_channel(owt_server_p2p_rpc_Address)
    owt_server_p2pStub = owt_server_p2p_pb2_grpc.LaunchStub(channel)
    response = owt_server_p2pStub.Start(owt_server_p2p_pb2.LaunchRequest(processName="node.exe"))
    check_state(response.result=="OK", response.message, owt_server_p2pStub, None, None)

#---------------Remote Launch Display-------------------------------
    channel = grpc.insecure_channel(display_rpc_Address)
    displayStub = display_pb2_grpc.LaunchStub(channel)
    response = displayStub.Start(display_pb2.LaunchRequest(ControlSignalEndpoint_STAGE=ControlSignalEndpoint_STAGE,
                                                           CodeMappingEndpoint_STAGE=CodeMappingEndpoint_STAGE,
                                                           SignalingServer=SignalingServer,
                                                           processName="DisplayWPF.exe"))
    check_state(response.result=="OK", response.message, owt_server_p2pStub, displayStub, None)

#---------------Remote Launch clumsy--------------------------------
    channel = grpc.insecure_channel(clumsy_rpc_Address)
    clumsyStub = clumsy_pb2_grpc.LaunchStub(channel)
    response = clumsyStub.Start(clumsy_pb2.LaunchRequest(args=config['Clumsy']['ARGS'], 
                                                         processName="clumsy.exe"))
    check_state(response.result=="OK", response.message, owt_server_p2pStub, displayStub, clumsyStub)

#---------------Local Launch web client----------------------------
    driver = owtClient.launch(currentDir+"/../../owt-client-javascript/peercall.html", "Entire screen", ControlSignalEndpoint_STAGE, 
                                                                                                        CodeMappingEndpoint_STAGE,
                                                                                                        SignalingServer)
    check_process("chrome.exe", "Launch owt-client-javascript failure", owt_server_p2pStub, displayStub, clumsyStub)
    return driver, owt_server_p2pStub, displayStub, clumsyStub

#Launch diplay, owt server, clumsy and web client and then start p2p sharing
def startSharing(currentDir, waitTime):
    driver, owt_server_p2pStub, displayStub, clumsyStub = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    owtClient.startShare(driver, "0000")
    result = owtClient.waitStreamReady(driver, waitTime)
    check_state(result, "wait for stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    return driver, owt_server_p2pStub, displayStub, clumsyStub, result

#-------------------Test Cases-------------------------------------
#Check current webrtc using h264 codec
def test_check_h264_codec_func():
    driver, owt_server_p2pStub, displayStub, clumsyStub, result = startSharing(currentDir, waitTime)
    strStats = owtClient.getStats(driver)
    while strStats == '':
          strStats = owtClient.getStats(driver)
    stats = json.loads(strStats)
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           assert Module.check_h264_codec_type(stat['codecId']) is True
    close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)

#Check if we can detect otp typing error
def test_check_otp_fail_func():
    driver, owt_server_p2pStub, displayStub, clumsyStub = launch_env(currentDir)
    result = owtClient.waitDisplayReady(driver)
    check_state(result, "wait for display stream ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    result = owtClient.loginAndWaitReady(driver)
    check_state(result, "wait for login ready fail", owt_server_p2pStub, displayStub, clumsyStub)
    owtClient.startShare(driver, "1234")
    assert owtClient.waitforOTPfail(driver) is True
    close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)

#Check we can detect screen sharing is stopped after clicking Stop
#The method is to get the same timestamp from 2 sequential stat reports in a specified interval
#If the video is stopped, the stat report are all the same
def test_check_stopped_func():
    driver, owt_server_p2pStub, displayStub, clumsyStub, result = startSharing(currentDir, waitTime)
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

'''
# dump webrtc stats after interpolating clumsy lag, drop, throttle parameters
def test_clumsy_dump_func():
    path = currentDir + "/statsDump"
    try:
      Path(path).mkdir(parents=True, exist_ok=True)
    except OSError:
      print ("Creation of the directory %s failed" % path)
      assert False

    for i in range(100, -10, -10):
      for j in range(30, -3, -3):
        for k in range(30, -3, -3):
            fileName = "l"+str(i)+"_d"+ str(j)+"_t"+ str(k)
            if not os.path.exists(path+"/"+fileName+".txt"):
                lagTime = i #0-3000
                dropChance = j #0-100
                throttleChance = k #0-100
                config['Clumsy']['ARGS'] = '--filter "udp and inbound" --lag on --lag-inbound on --lag-time ' + str(lagTime) + \
                                                               ' --drop on --drop-inbound on --drop-chance ' + str(dropChance)+ \
                                                               ' --throttle on --throttle-inbound on --throttle-chance ' + str(throttleChance)
                result = False
                while result == False:
                  driver, owt_server_p2pStub, displayStub, clumsyStub, result = startSharing(currentDir, 20)
                owtClient.launchAndPlayFullScreenVideo(currentDir+"/../../owt-client-javascript/fullscreen_video.html")
                time.sleep(10) #wait for 10 seconds and get dump stats
                strStats = owtClient.getStats(driver)
                while strStats == '':
                      strStats = owtClient.getStats(driver)
                fp = open(path+"/"+fileName+".txt", "w")
                fp.write(strStats)
                fp.close()
                close_all_instances(owt_server_p2pStub, displayStub, clumsyStub)
    assert True
'''