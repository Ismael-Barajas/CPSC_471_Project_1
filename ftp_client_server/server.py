#!/usr/bin/env python3
from socket import *
from subprocess import PIPE
import subprocess
import sys
import threading
import os

FORMAT = "utf-8"
MESSAGE_SIZE = 1024
RESPONSE_SIZE = 4096


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
        return self.socket.getsockname()[1]

    def waitForClient(self):
        print(f"Waiting for client {self.getPortNumber()}")
        portNumber = self.getPortNumber()
        self.cSocket.send(str(portNumber).encode(FORMAT))
        (cSocket, address) = self.socket.accept()
        self.cSocket = cSocket


def operations(data, cSocket):
    to_string = data.decode(FORMAT)
    operation = to_string.split()

    if operation[0] == "exit":
        print(f"Client had disconnected")

    elif operation[0] == "ls":
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)
        try:
            ephemeralConnection.waitForClient()
        except:
            print(f"Connection failed")
            return
        ephemeralConnection.cSocket.send(
            str.encode(
                f"{subprocess.run(['ls', './server_files'], stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout}"
            )
        )
        print(f"ls command completed")

    elif operation[0] == "get":
        fName = operation[1]
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)
        try:
            ephemeralConnection.waitForClient()
        except:
            print(f"Connection failed")
            return

        if not os.path.exists(os.path.join("server_files", fName)):
            print(
                f"File '{fName}' client is looking to download does not exist in the 'server_files' folder."
            )

        with open(os.path.join("server_files", fName), "rb") as f:
            ephemeralConnection.cSocket.sendall(f.read())

        print(
            f"{fName} has been transferred to the client. SIZE: {os.path.getsize(os.path.join('server_files', fName))} bytes transferred."
        )

    elif operation[0] == "put":
        fName = operation[1]
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)
        try:
            ephemeralConnection.waitForClient()
        except:
            print(f"Connection failed")
            return

        print("put made it past try block")

        tempData = b""
        fSize = None
        with open(os.path.join("server_files", fName), "wb") as f:
            while True:
                part = ephemeralConnection.cSocket.recv(RESPONSE_SIZE)
                tempData += part
                if len(part) < RESPONSE_SIZE:
                    fSize = tempData
                    f.write(tempData)
                    break
            f.close()

        print(
            f"{fName} has been transferred to server files. SIZE: {len(fSize)} bytes transferred."
        )

    else:
        print("Operation data not available")


def cHelper(cSocket, address):
    print(f"Connected from {address}")

    data = b""
    while True:
        part = cSocket.recv(MESSAGE_SIZE)
        data += part
        if len(part) < MESSAGE_SIZE:
            threading.Thread(target=operations, args=(data, cSocket)).start()
            if data.decode(FORMAT) == "exit":
                break
            data = b""


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
