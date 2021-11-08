#!/usr/bin/env python3
from socket import *
import sys
import os

FORMAT = "utf-8"
PORT_SIZE = 10
RESPONSE_SIZE = 4096


def main():
    # Pull localhost IP or url and the port number from the command line
    cIP = sys.argv[1]
    cPortNumber = int(sys.argv[2])

    # Create socket connection with server.py
    cSocket = socket(AF_INET, SOCK_STREAM)
    cSocket.connect((cIP, cPortNumber))

    print(f"Connected to server at: {cIP}:{cPortNumber}")

    while 1:
        # Splits user input by white space into a list
        command = input("ftp> ").split()

        if command[0] == "quit":
            # Check to see if any other arguments are passed with quit
            if len(command) != 1:
                print(
                    f"Please make sure there are no other arguments when using 'quit' command\n"
                )
            else:
                # Join list back into a string and send encoded string to server
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                # Close main connection with server
                cSocket.close()

                print(
                    f"Disconnecting from the server and shutting down the client. Bye!"
                )

                # Terminate script
                sys.exit(0)

        elif command[0] == "ls":
            # Check to see if any other arguments are passed with ls
            if len(command) != 1:
                print(
                    "Please make sure there are no other arguments when using ls command\n"
                )
            else:
                # Join list back into a string and send encoded string to server
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                # Method used to ensure every byte is received from the server
                data = b""
                while True:
                    part = cSocket.recv(PORT_SIZE)
                    data += part
                    if len(part) < PORT_SIZE:
                        break

                # Decode the port number of the ephemeral socket created in the server
                ephemeralSocketPortNumberDecoded = int(data.decode(FORMAT))

                # Establish connection with ephemeral socket to begin receiving info from the server
                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))

                print(
                    f"Connection established with ephemeral socket at {cIP}:{ephemeralSocketPortNumberDecoded}\n"
                )

                # Method used to ensure every byte is received from the ephemeral socket created in the server
                data = b""
                while True:
                    part = ephemeralSocket.recv(RESPONSE_SIZE)
                    data += part
                    if len(part) < RESPONSE_SIZE:
                        break

                # Decode received data from the ephemeral socket and display to client
                dataDecoded = data.decode(FORMAT)

                # Close connection with the ephemeral socket
                ephemeralSocket.close()

                # Display "ls" respose from server to client
                print(f"{dataDecoded}")

        elif command[0] == "get":
            # Check to see if there is only 1 additional argument passed with get
            if len(command) != 2:
                print(
                    "Please make sure there are no more than 1 argument when using get command\n"
                )
            else:
                # Pull file name from cli
                fName = command[1]

                # Join list back into a string and send encoded string to server
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                # Method used to ensure every byte is received from the ephemeral socket created in the server
                data = b""
                while True:
                    part = cSocket.recv(PORT_SIZE)
                    data += part
                    if len(part) < PORT_SIZE:
                        break

                # Decode the port number of the ephemeral socket created in the server
                ephemeralSocketPortNumberDecoded = int(data.decode(FORMAT))

                # Establish connection with ephemeral socket to begin receiving info from the server
                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))

                print(
                    f"Connection established with ephemeral socket at {cIP}:{ephemeralSocketPortNumberDecoded}"
                )

                # Method used to ensure every byte is received from the ephemeral socket created in the server then written
                data = b""
                # Open fName locally, "wb" open file for writing in binary mode
                with open(fName, "wb") as f:
                    while True:
                        part = ephemeralSocket.recv(RESPONSE_SIZE)
                        data += part
                        # If there is no respose from the server then the file does not exist.
                        if data == b"":
                            print(f"Server has no file with the name of '{fName}'")
                            break
                        # Once all data is receive execute this block of code
                        if len(part) < RESPONSE_SIZE:
                            # Write data to file
                            f.write(data)
                            print(
                                f"{len(data)} bytes have been successfully received from the server."
                            )
                            break
                    # Close the file once the data has been written
                    f.close()

                # If the file does not exist on the server, delete created file locally that was created in anticipation of the file data
                if data == b"":
                    os.remove(fName)

                # Close connection with the ephemeral socket
                ephemeralSocket.close()

        elif command[0] == "put":
            # Check to see if there is only 1 additional argument passed with put
            if len(command) != 2:
                print(
                    "Please make sure there are no more than 1 argument when using put command\n"
                )
            else:
                # Pull file name from cli
                fName = command[1]

                # Check to see if provided file name exist in current directory
                if not os.path.exists(fName):
                    print(f"{fName} does not exist or not found in current directory.")
                    continue

                # Join list back into a string and send encoded string to server
                commandString = " ".join(command)
                cSocket.send(commandString.encode(FORMAT))

                # Method used to ensure every byte is received from the ephemeral socket created in the server
                data = b""
                while True:
                    part = cSocket.recv(PORT_SIZE)
                    data += part
                    if len(part) < PORT_SIZE:
                        break

                # Decode the port number of the ephemeral socket created in the server
                ephemeralSocketPortNumberDecoded = int(data.decode(FORMAT))

                # Establish connection with ephemeral socket to begin receiving info from the server
                ephemeralSocket = socket(AF_INET, SOCK_STREAM)
                ephemeralSocket.connect((cIP, ephemeralSocketPortNumberDecoded))

                print(
                    f"Connection established with ephemeral socket at {cIP}:{ephemeralSocketPortNumberDecoded}"
                )

                # Open fName locally, "rb" open file for reading in binary mode
                with open(fName, "rb") as f:
                    # Send all the file's data to ephemeral socket on the server
                    ephemeralSocket.sendall(f.read())

                # Close connection with the ephemeral socket
                ephemeralSocket.close()

                # Display number of bytes transferred to server
                print(
                    f"{os.path.getsize(fName)} bytes have been successfully transferred to the server."
                )

        # If an invalid command passed then execute this
        else:
            print(
                f"Invalid command. Commands available: ls, get <filename>, put <filename>, quit\n"
            )


if __name__ == "__main__":
    main()
