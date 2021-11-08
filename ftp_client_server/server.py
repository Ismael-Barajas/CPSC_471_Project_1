#!/usr/bin/env python3
from socket import *
import subprocess
import sys
import threading
import os

FORMAT = "utf-8"
MESSAGE_SIZE = 1024
RESPONSE_SIZE = 4096

# Helper Class to manage the ephemeral socket
class ephemeralSocket:
    # Initialize passed in vairables to be accessed through out the class instance
    def __init__(self, cSocket, content=None, timeout=60):
        self.cSocket = cSocket
        self.timeout = timeout
        self.content = content
        self.create_listen()

    #  Function that creates ephemeralSocket and listen for connection
    def create_listen(self):
        self.ephemeralSocket = socket(AF_INET, SOCK_STREAM)

        # Set timeout in seconds, if timeout time is exceeded then and exception is thrown, if no timeout time is provided the default is 60s
        self.ephemeralSocket.settimeout(self.timeout)
        self.ephemeralSocket.bind(("", 0))
        self.ephemeralSocket.listen(1)

    # Function that waits for client to connect to the ephemeral socket instance
    def wait(self):
        print(f"Waiting for client on port: {self.ephemeralSocket.getsockname()[1]}")

        # Pull port number from the ephemeral socket instance and send it to client so they can connect to it
        portNumber = self.ephemeralSocket.getsockname()[1]
        self.cSocket.send(str(portNumber).encode(FORMAT))

        # Wait for client to connect to ephemeral socket instance
        (cSocket, address) = self.ephemeralSocket.accept()

        # Once a connection is made create a client socket variable available to freely send and receive messages/data
        self.cSocket = cSocket


def operations(data, cSocket):
    # Decode and split operation message received from the client
    to_string = data.decode(FORMAT)
    operation = to_string.split()

    if operation[0] == "quit":
        # Client has disconnected from server
        print(f"Client had disconnected")

    elif operation[0] == "ls":
        # Create an ephemeral socket instance providing the client socket and timeout time of 3 seconds
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)

        try:
            # Wait for TIMEOUT seconds for client to connect to ephemeral socket
            ephemeralConnection.wait()
        except:
            # If timeout exception is thrown, return and abort operation
            print(f"Connection failed")
            return

        # Send the ls command results to client
        ephemeralConnection.cSocket.send(
            str.encode(
                f"{subprocess.run(['ls', './server_files'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout}"
            )
        )
        print(f"'ls' command executed.")

    elif operation[0] == "get":
        # Pull file name client provided message
        fName = operation[1]

        # Create an ephemeral socket instance providing the client socket and timeout time of 3 seconds
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)

        try:
            # Wait for TIMEOUT seconds for client to connect to ephemeral socket
            ephemeralConnection.wait()
        except:
            # If timeout exception is thrown, return and abort operation
            print(f"Connection failed")
            return

        # Check to see if provided file name exist in "server_files" directory
        if not os.path.exists(os.path.join("server_files", fName)):
            print(
                f"File '{fName}' client is looking to download does not exist in the 'server_files' folder."
            )
            return

        # Open fName in "server_files" directory, "rb" open file for reading in binary mode
        with open(os.path.join("server_files", fName), "rb") as f:
            # Send all file data to client
            ephemeralConnection.cSocket.sendall(f.read())

        # Display file and file size transferred to client
        print(
            f"{fName} has been transferred to the client. SIZE: {os.path.getsize(os.path.join('server_files', fName))} bytes transferred."
        )
        print(f"'get' command executed.")

    elif operation[0] == "put":
        # Pull file name client provided message
        fName = operation[1]

        # Create an ephemeral socket instance providing the client socket and timeout time of 3 seconds
        ephemeralConnection = ephemeralSocket(cSocket, timeout=3)

        try:
            # Wait for TIMEOUT seconds for client to connect to ephemeral socket
            ephemeralConnection.wait()
        except:
            # If timeout exception is thrown, return and abort operation
            print(f"Connection to ephemeral socket failed.")
            return

        # Method used to ensure every byte is received from client
        tempData = b""
        fSize = None
        # Open/create a file named fName in the "server_files" directory, "wb" open file for writing in binary mode
        with open(os.path.join("server_files", fName), "wb") as f:
            while True:
                part = ephemeralConnection.cSocket.recv(RESPONSE_SIZE)
                tempData += part
                # Once all data is receive execute this block of code
                if len(part) < RESPONSE_SIZE:
                    # Save file to fSize to display file size outside of this loop
                    fSize = tempData
                    # Write data to file
                    f.write(tempData)
                    break
            # Close the file once the data has been written
            f.close()

        # Display file and file size transferred from client to server
        print(
            f"{fName} has been transferred to server files. SIZE: {len(fSize)} bytes transferred."
        )
        print(f"'put' command executed.")

    # If operation/command is not available, execute this
    else:
        print(f"{operation[0]} not available")


# Helper function to receive messages from client
def commandOperationsHelper(cSocket, address):
    print(f"Connected from {address}")

    # Method used to ensure every byte is received from the client
    data = b""

    # Forever listen for client messages to run commands until connection is terminated
    while True:
        part = cSocket.recv(MESSAGE_SIZE)
        data += part
        if len(part) < MESSAGE_SIZE:
            # Create a thread to execute client's command
            threading.Thread(target=operations, args=(data, cSocket)).start()

            # If client wants to terminate connection with server, break this loop to finally terminate the client thread created in main() to prevent looping errors
            if data.decode(FORMAT) == "quit":
                break

            # Reset message buffer
            data = b""


def main():
    # Check to see if an IP address & port number are provided
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} <port number>")
        return

    # Pull port number provided
    sPortNumber = int(sys.argv[1])

    # Create socket and bind server port number to server socket
    sSocket = socket(AF_INET, SOCK_STREAM)
    sSocket.bind(("", sPortNumber))

    # Socket now listens for a connection from client with a backlog length of 5 (length of the queue of pending connections allow to this socket)
    sSocket.listen(5)

    print(f"Starting server on port {sPortNumber}")

    while 1:
        # Pull info from connected client
        (cSocket, address) = sSocket.accept()

        # Create a thread for client(s) connected to start receiving commands
        threading.Thread(
            target=commandOperationsHelper, args=(cSocket, address)
        ).start()


if __name__ == "__main__":
    main()
