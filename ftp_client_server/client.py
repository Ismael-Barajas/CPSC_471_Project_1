#!/usr/bin/env python3
from socket import *
import sys
import os

FORMAT = "utf-8"
MESSAGE_SIZE = 1024
PORT_SIZE = 10
RESPONSE_SIZE = 4096


def main():
    # Pull localhost IP or url and the port number from the command line
    cIP = sys.argv[1]
    cPortNumber = int(sys.argv[2])
    # Create socket connection with server.py
    cSocket = socket(AF_INET, SOCK_STREAM)
    cSocket.connect((cIP, cPortNumber))
    print(f"connected to {cIP}:{cPortNumber}")

    while 1:
        # Splits user input by white space into a list
        command = input("ftp> ").split()

        if command[0] == "ls":
            # Check to see if any other arguments are passed with ls
            if len(command) != 1:
                print(
                    "Please make sure there are no other arguments when using ls command\n"
                )
            else:
                # " ".join(command)
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                data = bytearray()
                while len(data) < PORT_SIZE:
                    packet = cSocket.recv(PORT_SIZE - len(data))
                    if not packet:
                        return None
                    data.extend(packet)
                ephemeralSocketPortNumber = data

                ephemeralSocketPortNumberDecoded = int(
                    ephemeralSocketPortNumber.decode(FORMAT)
                )

                print(f"Ephemeral port {ephemeralSocketPortNumberDecoded}")

                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))
                data = bytearray()
                while len(data) < RESPONSE_SIZE:
                    packet = cSocket.recv(RESPONSE_SIZE - len(data))
                    if not packet:
                        return None
                    data.extend(packet)
                dataDecoded = data.decode(FORMAT)
                print(f"{dataDecoded}")


if __name__ == "__main__":
    main()
