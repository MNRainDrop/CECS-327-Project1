# CECS 327 - Group Project 1 A Bite of Distributed Communication

## How to use the program

1. Run server.py on one machine.
2. Run client.py on another machine on the local network, a virtual machine, or in another command prompt.
3. In the Client, input the IP address of the Server that is printed in the console of Server.
4. Run a command using the following structure `/{command} {args}`
   * To stop any running clients, use the `/stop` command
   * To stop the server, use the `/stop` command

## Server Commands

### `/stop`

Forcibly shuts down the server. Notifies the clients that the server will be closed.

### `/broadcast {args}`

Broadcasts a message to every client connected to the server.

### `/list`

Lists all clients connected to the server.

## Client Commands

### `/stop`

Shuts down the connection between the server and the client. Also closes the client.

### `/broadcast {args}`

Broadcasts a message to every client connected to the server as well as to the server.

### `/list`

Lists all clients connected to the server.

### `/join {args}`

Subscribes to a chat room

{args} - name of the chat room

### `/msg {args0} {args1}`

Sends a message to a chat room

{args0} - name of chat room

{args1} - message to be sent to the chat room
