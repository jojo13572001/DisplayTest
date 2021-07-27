# Introduction 
* The reposity is to automation test owt p2p connection between owt-server-p2p, owt-client-javascript and owt-client-native. Test cases include codec info, otp typing, video control.
* It also dumps webrtc stat report during video playing for future analysis.

# Prerequisite
* Install [Python >= 3.6](https://www.python.org/downloads/). I use 3.6.9
* Install [pip 2.21.1](https://pip.pypa.io/en/stable/installation/#get-pip-py) python get-pip.py
* Install [Nodejs 14.16.1](https://nodejs.org/ja/blog/release/v14.16.1/) x64

# Auto Test
1. execute owt-server-p2p/launchRpc.bat, DisplayWPF_Net47/launchRpc.bat, clumsy/launchRpc.bat (admin mode) to launch RPC agents  
2. fill agent addresses in step1 to config.ini at the same host with auto_test.cmd
3. execute auto_test.cmd  

# Folder structure
* **.pipeline**  
     **---  azure-pipelines.yml** &nbsp;     &nbsp;support azure pipeline automation test of local files. It also support downloading remote .msi for automation test
* DisplayWPF_Net47  
     **---  launch.bat** &nbsp;     &nbsp;launch current instance(DisplayWPF.exe)  
     **---  launchRpc.bat** &nbsp;     &nbsp;launch RPC agent to control life cycle of current instance  
     **---  service.py** &nbsp;     &nbsp;RPC services that include start(launch.bat) and terminate current instance  
     **---  _ main _.py** &nbsp;     &nbsp;specify RPC port
* **[clumsy](https://github.com/jagt/clumsy)**
* **[owt-server-p2p](https://github.com/open-webrtc-toolkit/owt-server-p2p)**  
     **---  config.json** &nbsp;     &nbsp;specify owt-server-p2p socketIO port, control signal server port and code mapping server port(the same with control signal server)
* **[owt-client-javascript](https://github.com/open-webrtc-toolkit/owt-client-javascript)**  
     **--  fullscreen_video.html** &nbsp;     &nbsp;for test_clumsy_dump_func test case to screen sharing with youtube content
* **pytest**  
&nbsp;     &nbsp;**tests**  
&nbsp;            &nbsp;**---  owtClient.py** &nbsp;     &nbsp;owt-client-javascript related control functionality  
&nbsp;            &nbsp;**---  test_display.py** &nbsp;     &nbsp;all test cases to control owt-client-javascript through owtClient.py
* **proto**  
     **---  build.bat** &nbsp;     &nbsp;auto build rpc protobuf of DisplayWPF_Net47, clumsy and owt-server-p2p
* **auto_test.cmd** &nbsp;     &nbsp;remote launch all instances and control automation test
* **config.ini** &nbsp;     &nbsp;record each RPC ip and port. It should be synchronous with all _ main _.py and config.json

# Instance Architecture
<image src="owt-client-javascript/pic/Architecture.png">
    
# Connection Flow
<image src="owt-client-javascript/pic/test_clumsy_dump_func_flow.png">

# Data Transmit Flow
<image src="owt-client-javascript/pic/test_clumsy_dump_func_sequence.png">