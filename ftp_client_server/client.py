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

        if command[0] == "exit":
            # Check to see if any other arguments are passed with exit
            if len(command) != 1:
                print(
                    f"Please make sure there are no other arguments when using exit command\n"
                )
            else:
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                cSocket.close()

                print(
                    f"Disconnecting from the server and shutting down the client. Bye!"
                )
                sys.exit(0)

        elif command[0] == "ls":
            # Check to see if any other arguments are passed with ls
            if len(command) != 1:
                print(
                    "Please make sure there are no other arguments when using ls command\n"
                )
            else:
                # " ".join(command)
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                data = b""
                while True:
                    part = cSocket.recv(PORT_SIZE)
                    data += part
                    if len(part) < PORT_SIZE:
                        break

                ephemeralSocketPortNumberDecoded = int(data.decode(FORMAT))

                print(f"Ephemeral port {ephemeralSocketPortNumberDecoded}")

                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))

                data = b""
                while True:
                    part = ephemeralSocket.recv(RESPONSE_SIZE)
                    data += part
                    if len(part) < RESPONSE_SIZE:
                        break
                dataDecoded = data.decode(FORMAT)
                print(f"{dataDecoded}")

        elif command[0] == "get":
            # Check to see if there is only 1 additional argument passed with get
            if len(command) != 2:
                print(
                    "Please make sure there are no more than 1 argument when using get command\n"
                )
            else:
                fName = command[1]

                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                data = b""
                while True:
                    part = cSocket.recv(PORT_SIZE)
                    data += part
                    if len(part) < PORT_SIZE:
                        break

                ephemeralSocketPortNumberDecoded = int(data.decode(FORMAT))

                print(f"Ephemeral port {ephemeralSocketPortNumberDecoded}")

                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))

                data = b""
                with open(fName, "wb") as f:
                    while True:
                        part = ephemeralSocket.recv(RESPONSE_SIZE)
                        data += part
                        if data == b"":
                            print(f"Server has no file with the name of '{fName}'")
                            break
                        if len(part) < RESPONSE_SIZE:
                            f.write(data)
                            print(
                                f"{len(data)} bytes have been successfully received from the server."
                            )
                            break
                    f.close()
                if data == b"":
                    os.remove(fName)
                ephemeralSocket.close()

        elif command[0] == "put":
            # Check to see if there is only 1 additional argument passed with put
            if len(command) != 2:
                print(
                    "Please make sure there are no more than 1 argument when using put command\n"
                )
            else:
                # pull file name from cli
                fName = command[1]

                if not os.path.exists(fName):
                    print(f"{fName} does not exist or not found in current directory.")
                    continue

                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                data = b""
                while True:
                    part = cSocket.recv(PORT_SIZE)
                    data += part
                    if len(part) < PORT_SIZE:
                        break

                ephemeralSocketPortNumberDecoded = int(data.decode(FORMAT))

                print(f"Ephemeral port {ephemeralSocketPortNumberDecoded}")

                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))

                with open(fName, "rb") as f:
                    ephemeralSocket.sendall(f.read())

                ephemeralSocket.close()

                print(
                    f"{os.path.getsize(fName)} bytes have been successfully transferred to the server."
                )

        else:
            print(
                f"Invalid command. Commands available: ls, get <filename>, put <filename>, exit\n"
            )


if __name__ == "__main__":
    main()
