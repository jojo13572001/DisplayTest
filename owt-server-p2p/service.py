# service.py
import os
import subprocess
import time
from concurrent import futures
import grpc
import owt_server_p2p_pb2_grpc, owt_server_p2p_pb2

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
        owt_server_p2p_pb2_grpc.add_LaunchServicer_to_server(Servicer(), server)
        server.add_insecure_port('[::]:'+ port)
        server.start()
        server.wait_for_termination()

class Servicer(owt_server_p2p_pb2_grpc.LaunchServicer):

    def Start(self, request, context):
        currentDir = os.path.dirname(os.path.realpath(__file__))
        os.system(currentDir + "/launch.bat")
        time.sleep(waitTime)
        result = check_process(request.processName)
        if result == True:
           return owt_server_p2p_pb2.Reply(result='OK', message="")
        else:
           return owt_server_p2p_pb2.Reply(result='Fail', message=request.processName + " launch fail")

    def Terminate(self, request, context):
        os.system('taskkill /f /im ' + request.processName)
        time.sleep(waitTime)
        resultNode = check_process(request.processName)
        if resultNode == False:
           return owt_server_p2p_pb2.Reply(result='OK', message="")
        else:
           return owt_server_p2p_pb2.Reply(result='Fail', message=request.processName + " terminate Failure. It still exists.")