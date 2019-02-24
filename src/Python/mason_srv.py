# -*- coding: utf-8 -*-

# If python 2.7, use SocketServer.
# Otherwise 3.6, please use socketserver.
# import SocketServer as SockServ
import socketserver as SockServ
import socket

import os
import time
import json

import mason_main as wshm


def create_lockfile():
    dir = os.path.dirname(os.path.abspath(__file__))
    pid = os.getpid()

    lockFile = open(os.path.join(dir, 'srv.lock'), 'w')
    lockFile.write(str(pid) + "\n")
    lockFile.close()


#HOST, PORT = "127.0.0.1", 60031

class SampleHandler(SockServ.BaseRequestHandler, object):

    def handle(self):

        client = self.request

        message = client.recv(65536)
        reqJson = json.loads(message)

        # Processing Entity
        resJson = wshm.SocketExecute(reqJson)
        json_dumps = json.dumps(resJson, separators=(',', ':'))

        # if reqJson["reqCode"] == -1 :
        #     server.server_close()

        self.request.send( json_dumps.encode())


class SampleServer(SockServ.ThreadingTCPServer, object):
    def server_bind(self):
        self.xxx = object
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

if __name__ == "__main__":

    create_lockfile()

    dir = os.path.dirname(os.path.abspath(__file__))
    paramFile = open(os.path.join(dir, 'mason_param.json'), 'r')
    jsonParam = json.load(paramFile)

    port = jsonParam['port']
    host = jsonParam['host']
    print("port : " + str(port))
    print("host : " + host)

    wshm.Init()

    try:
        server = SampleServer((host, port), SampleHandler)
        print("[mason] stand-by.")
        server.serve_forever()
    finally:
        os.remove(os.path.join(dir, 'srv.lock'))
