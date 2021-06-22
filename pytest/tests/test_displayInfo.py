from libs.module import Module
import time
import os
import owtClient
import subprocess
import sys
import json

waitTime = 5
#---------------Close All Tested Server and Clients-----------
def close_all_instances():
	os.system('taskkill /f /im chrome.exe')
	os.system('taskkill /f /im DisplaySubprocess.exe')
	os.system('taskkill /f /im DisplayWPF.exe')
	os.system('taskkill /f /im node.exe')

def check_process(processName, errorMessage):
	progs = str(subprocess.check_output('tasklist'))
	if processName not in progs:
	   print(errorMessage)
	   close_all_instances()
	   sys.exit(0)

#---------------Set Environment Variables--------------------
os.environ["ControlSignalEndpoint_STAGE"] = "https://localhost:8098"
os.environ["CodeMappingEndpoint_STAGE"] = "https://localhost:8096"
os.environ["SignalingServer"] = "https://localhost:8096"

currentDir = os.path.dirname(os.path.realpath(__file__))

#---------------Launch p2p servers---------------------------
os.system(currentDir+"/../../owt-server-p2p/launch.bat")
time.sleep(waitTime)
check_process("node.exe", "Launch owt-server-p2p failure")

#---------------Launch Display-------------------------------
os.system(currentDir+"/../../DisplayWPF_Net47/launch.bat")
time.sleep(waitTime)
check_process("DisplayWPF.exe", "Launch DisplayWPF failure")

#---------------Launch web client----------------------------
driver = owtClient.launch(currentDir+"/../../owt-client-javascript/peercall.html", "Entire screen")
check_process("chrome.exe", "Launch owt-client-javascript failure")

#---------------Start automation-----------------------------
owtClient.waitDisplayReady(driver)
owtClient.loginAndWaitReady(driver)
owtClient.startShare(driver)
owtClient.waitStreamReady(driver)
strStats = owtClient.getStats(driver)
while strStats is '':
	strStats = owtClient.getStats(driver)
stats = json.loads(strStats)

#-------------------Test Cases-------------------------------
def test_check_h264_codec_func():
    for stat in stats:
        if stat['type'] == "inbound-rtp":
           assert Module.check_h264_codec_type(stat['codecId']) is True

close_all_instances()