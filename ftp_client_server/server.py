#!/usr/bin/env python3
from socket import *
from subprocess import PIPE
import subprocess
import sys
import threading
import os

FORMAT = "utf-8"
MESSAGE_SIZE = 1024


class ephemeralSocket:
    def __init__(self, cSocket, content=None, timeout=60):
        self.cSocket = cSocket
        self.timeout = timeout
        self.content = content

        self._listen()

    def _listen(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.bind(("", 0))
        self.socket.listen(1)

    def getPortNumber(self):
        return self.socket.getpeername()[1]

    def waitForClient(self):
        print(f"Waiting for client {self.getPortNumber()}")
        portNumber = self.getPortNumber()
        self.cSocket.send(portNumber.encode(FORMAT))
        (cSocket, address) = self.socket.accept()
        self.cSocket = cSocket


def operations(data, cSocket):
    to_string = data.decode(FORMAT)
    operation = to_string.split()

    if operation[0] == "ls":
        print("made it to ls")
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)
        print("after ephemeralConnection")
        try:
            ephemeralConnection.waitForClient()
        except:
            print(f"Connection failed")
            return
        ephemeralConnection.cSocket.send(
            str.encode(
                f"{subprocess.run(['ls', './files'], stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout}"
            )
        )
        print(f"ls command completed")

    else:
        print("Operation data not available")


def cHelper(cSocket, address):
    print(f"Connected from {address}")

    # data = bytearray()
    # while len(data) < MESSAGE_SIZE:
    #     packet = cSocket.recv(MESSAGE_SIZE - len(data))
    #     if not packet:
    #         return None
    #     data.extend(packet)
    data = b""
    while True:
        part = cSocket.recv(MESSAGE_SIZE)
        data += part
        if len(part) < MESSAGE_SIZE:
            break

    print(f"thread made in cHelper")
    threading.Thread(target=operations, args=(data, cSocket)).start()


def main():
    # Check to see if an IP address & port number are provided
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} <port number>")
        return
    # Pull port info and create connection
    sPortNumber = int(sys.argv[1])
    sSocket = socket(AF_INET, SOCK_STREAM)
    sSocket.bind(("", sPortNumber))
    sSocket.listen(5)
    print(f"Starting server on port {sPortNumber}")

    while 1:
        (cSocket, address) = sSocket.accept()
        threading.Thread(target=cHelper, args=(cSocket, address)).start()


if __name__ == "__main__":
    main()

"""
this is where I left off.
Starting server on port 12001
Connected from ('127.0.0.1', 53370)
thread made in cHelper
made it to ls
after ephemeralConnection
Connection failed"""
