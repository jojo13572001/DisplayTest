from libs.module import Module
import time
import os
import owtClient

#---------------Set Environment Variables--------------------
os.environ["ControlSignalEndpoint_STAGE"] = "https://localhost:8098"
os.environ["CodeMappingEndpoint_STAGE"] = "https://localhost:8096"
os.environ["SignalingServer"] = "https://localhost:8096"

#---------------Launch p2p servers and Display---------------
currentDir = os.path.dirname(os.path.realpath(__file__))
os.system(currentDir+"/../../owt-server-p2p/launch.bat")
time.sleep(3)

os.system(currentDir+"/../../DisplayWPF_Net47/launch.bat")
time.sleep(3)

#---------------Launch web client and start automation--------
driver = owtClient.launch(currentDir+"/../../owt-client-javascript/peercall.html", "Entire screen")
owtClient.waitDisplayReady(driver)
owtClient.loginAndWaitReady(driver)
owtClient.StartShare(driver)
owtClient.waitStreamReady(driver)
time.sleep(3)
stats = owtClient.GetStats(driver)

#-------------------Test Cases-----------------------------------
def test_check_h264_codec_func():
    for stat in stats:
       if stat['type'] == 'inbound-rtp':
          assert (stat['codecId'] == Module.get_codec_type()) is True

#---------------Close All Tested Server and Clients-----------
os.system('taskkill /f /im chrome.exe')
os.system('taskkill /f /im DisplaySubprocess.exe')
os.system('taskkill /f /im DisplayWPF.exe')
os.system('taskkill /f /im node.exe')

