# File Transfer Protocol Server & Client

## Group Members
- Ismael Barajas: ismaelbarajas30@csu.fullerton.edu
- Casey Thatsanaphonh: cthatsanaphonh@csu.fullerton.edu
-
-

## Programming Language
*Python 3.9 or newer*

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

