# service.py
import os
import subprocess
import time
from concurrent import futures
import grpc
import display_pb2_grpc, display_pb2

waitTime = 1
def check_process(processName):
    progs = str(subprocess.check_output('tasklist'))
    if processName not in progs:
       return False
    return True

class Server:

    @staticmethod
    def run(port):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        display_pb2_grpc.add_LaunchServicer_to_server(Servicer(), server)
        server.add_insecure_port('[::]:'+ port)
        server.start()
        server.wait_for_termination()

class Servicer(display_pb2_grpc.LaunchServicer):

    def Start(self, request, context):
        if request.ControlSignalEndpoint_STAGE != "" and \
           request.CodeMappingEndpoint_STAGE != "" and \
           request.SignalingServer != "":
           os.environ["ControlSignalEndpoint_STAGE"] = request.ControlSignalEndpoint_STAGE
           os.environ["CodeMappingEndpoint_STAGE"] = request.CodeMappingEndpoint_STAGE
           os.environ["SignalingServer"] = request.SignalingServer
           currentDir = os.path.dirname(os.path.realpath(__file__))
           os.system(currentDir + "/launch.bat")
           time.sleep(waitTime)
           result = check_process("DisplayWPF.exe")
           if result == True:
              return display_pb2.Reply(result='OK', message="")
           else:
              return display_pb2.Reply(result='Fail', message="DisplayWPF.exe launch fail")
        return display_pb2.Reply(result='Fail', message="server url is empty")

    def Terminate(self, request, context):
        if request.terminate == True:
           os.system('taskkill /f /im DisplaySubprocess.exe')
           os.system('taskkill /f /im DisplayWPF.exe')
           time.sleep(waitTime)
           resultDisplayWPF = check_process("DisplayWPF.exe")
           resultDisplaySubprocess = check_process("DisplaySubprocess.exe")
           if resultDisplayWPF == False and resultDisplaySubprocess == False:
              return display_pb2.Reply(result='OK', message="")
           else:
              return display_pb2.Reply(result='Fail', message="DisplayWPF.exe or DisplaySubprocess.exe terminate Failure. It still exists.")