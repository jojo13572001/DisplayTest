# service.py
import os
import subprocess
import time
from concurrent import futures
import grpc
import clumsy_pb2_grpc, clumsy_pb2

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
        clumsy_pb2_grpc.add_LaunchServicer_to_server(Servicer(), server)
        server.add_insecure_port('[::]:'+ port)
        server.start()
        server.wait_for_termination()

class Servicer(clumsy_pb2_grpc.LaunchServicer):

    def Start(self, request, context):
        currentDir = os.path.dirname(os.path.realpath(__file__))
        os.system(currentDir + "/launch.bat " + request.args)
        time.sleep(waitTime)
        result = check_process("clumsy.exe")
        if result == True:
           return clumsy_pb2.Reply(result='OK', message="")
        else:
           return clumsy_pb2.Reply(result='Fail', message="clumsy launch fail")

    def Terminate(self, request, context):
        if request.terminate == True:
           os.system('taskkill /f /im clumsy.exe')
           time.sleep(waitTime)
           resultNode = check_process("clumsy.exe")
           if resultNode == False:
              return clumsy_pb2.Reply(result='OK', message="")
           else:
              return clumsy_pb2.Reply(result='Fail', message="clumsy terminate Failure. It still exists.")