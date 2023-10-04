import socket
import threading
from globalVariables import *
import os

print(os.getpid())
exit_event = threading.Event()

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# creates socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.settimeout(0.5)
print("[Server] Socket created")

# bind to the port
server.bind(ADDR)
print(f"[Server] Server bound to {ADDR}")

# used to broadcast messages to clients
broadcast_message = []
# list of clients that are currently connected to the server
client_list = []

def handle_client(conn, addr):
    conn.setblocking(0)
    conn.settimeout(0.5)
    print(f"[Server] New connection : {addr}")
    connected = True
    # used to know what broadcasted messages the client has recieved
    recieved_messages = 0

    while connected:
        if exit_event.is_set():
            try:
                conn.send("[Server] Server shut down. You will be disconnected".encode(FORMAT))
            finally:
                disconnect_client(connected, conn, addr)
                break
        try:
            msg_len = conn.recv(MESSAGEHEADER).decode(FORMAT)
            if msg_len:
                msg_len = int(msg_len)
                msg = conn.recv(msg_len).decode(FORMAT)
                print(f"[{addr}] {msg}")

                try:
                    args = msg.split(maxsplit=1)[1]
                except:
                    args = None
                finally:
                    command = msg.split(maxsplit=1)[0].lower()
                
                if command == DISCONNECT_MESSAGE:
                    print(f"[{addr}] Client disconnected")
                    conn.send("[Server] Client disconnected".encode(FORMAT))
                    disconnect_client(connected, conn, addr)
                    break
                elif command == BROADCAST_MESSAGE:
                    broadcast(f"[{addr[1]}]", args)
                elif command == LIST_CLIENT_MESSAGE:
                    clients = ""
                    for i in range(len(client_list)):
                        clients += client_list[i] + "/n"
                    clients += client_list[len(client_list)]
                    conn.send(clients.encode(FORMAT))
        except:
            pass

        if len(broadcast_message) > recieved_messages:
            conn.send(f"{broadcast_message[recieved_messages][0]} {broadcast_message[recieved_messages][1]}".encode(FORMAT))
            print("[Server] Message Sent")
            recieved_messages += 1
        
    conn.close()
    print(f"[Server] Active Connections {len(client_list)}")

def disconnect_client(connected, conn, addr):
    connected = False
    client_list.remove(addr[1])
    conn.close()

def listen():
    # listen for connections
    server.listen()
    print(f"[Server] Server is listening on {SERVER}")
    listening = True
    while listening:
        if exit_event.is_set():
            print("[Server] No longer listening...")
            listening = False
            break
        try:
            # when connection is established create a new thread of handle_client
            conn, addr = server.accept()
            client_list.append(addr[1])
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[Server] Active Connections {threading.active_count() - 2}")
        except:
            pass

def broadcast(sender, message):
    broadcast_message.append((sender, message))
    print(f"{sender} {message}")

def start():
    # start listen thread
    listening = threading.Thread(target=listen)
    listening.start()
    
    run = True
    while run:
        cin = input()
        
        try:
            args = cin.split(maxsplit=1)[1]
        except:
            args = None
        finally:
            command = cin.split(maxsplit=1)[0]

        if command.lower() == DISCONNECT_MESSAGE and args == None:
            exit_event.set()
            listening.join()
            print("[Server] Server is stopping...")
            run = False
            break
        elif command.lower() == BROADCAST_MESSAGE:
            broadcast("[Server]", args)
        elif command == LIST_CLIENT_MESSAGE:
            clients = ""
            for x in client_list:
                clients += f"{x}\n" 
            print(clients, end='')
        else:
            print("Not a valid command")

print("[Server] Server is starting...")
start()