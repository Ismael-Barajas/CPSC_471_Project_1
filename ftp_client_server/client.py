#!/usr/bin/env python3
from socket import *
import sys
import os

ENCODE_FORMAT = "utf-8"


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
                cSocket.send(command.encode(ENCODE_FORMAT))


if __name__ == "__main__":
    main()
