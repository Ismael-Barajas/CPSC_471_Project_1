# File Transfer Protocol Server & Client

## Group Members

- Ismael Barajas: ismaelbarajas30@csu.fullerton.edu
- Casey Thatsanaphonh: cthatsanaphonh@csu.fullerton.edu
- Michael Lam: micheallam@csu.fullerton.edu
- Aidin Tavassoli: aidintavassoli@csu.fullerton.edu

## Protocol Design

### Client Side:
The protocol uses 2 different sockets on the client side:

1. cSocket : this is the clients control socket which establishes the connection with the servers listening port. Commands are sent through this socket.
2. ephemeralSocekt: this socket establishes a connection with the servers ephemeralSocket which is used to send/receive bytes.
   Control Channel: cSocket is the control channel and it transmits commands from the client to the server.
 ### Server Side:
  - ephemralSocket class is the helper class that manages the ephemeral socket using the functions below:
  - create_listen() function creates an ephemeral socket on which the server listens for connection.
  - wait() function allows the server to wait for connection from the epehrmeralSocket and accept connection from the client.
   Data received on the cSocket is decode by the operations() function and the server takes appropriate action based on the received command from the client on cSocket.
   Each operation creates an instance of ephemeralSocket object with a 3 second timeout and performs the operation requested by the client.

- Message: Message size is 1024 and the format is utf-8 with the response size of 4096.
- File Transfer Channel: client must receive the message containing the server’s ephemeral socket port number and decode it and then establish a connection using IP and the port number to begin receiving on that channel.
- Controlling Stop/Start Receiving Files: Keeping track of response size inside of a loop allows us to receive the file in chunks and works like a TCP buffer which receives up to a predetermined (hard coded) maximum response size and the append to the file then continues to receive the remainder of the file in the same manner until the sender stops sending.

## FTP Diagram: 
![alt text](https://i.imgur.com/g094r0x.png)

## Programming Language

_Python 3.8.10 or newer_

## How to Run Program

### First Start Server

```
./server.py <port_number>
```

### Then Start Client

```
./client.py <IP/server_machine> <port_number>
```

### Client Commands Available

**get**

```
ftp> get <filename>
```

Downloads \<filename\> from the server. ( /server_files directory )

**put**

```
ftp> put <filename>
```

Uploads \<filename\> to the server. ( /server_files directory )

**ls**

```
ftp> ls
```

Lists all files on the server. ( /server_files directory )

**quit**

```
ftp> quit
```

Disconnects Client from the server and terminates Client.py script.
