import socket
import threading
import time
import pandas as pd
from globalVariables import *
import os

print(os.getpid())
exit_event = threading.Event()

df = pd.DataFrame({'Type':[], 'Time(s)':[], 'Source_IP':[], 'Destination_IP':[], 'Source_Port':[], 'Destination_Port':[], 'Length(bytes)':[]})
starttime = time.time()
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

#create groups for multicast to put the clients in
client_groups = []

# list of clients that are currently connected to the server
client_list = []

def handle_client(conn, addr):
    conn.setblocking(0)
    conn.settimeout(0.5)
    print(f"[Server] New connection : {addr}")
    connected = True
    # used to know what broadcasted messages the client has recieved
    recieved_messages = 0
    # joined groups
    joined_groups = []

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
                    broadcast(addr, args)

                if command == JOIN_GROUP:
                    join_group(addr, args)
                    joined_groups.append([args, 0])
                    conn.send(f"Successfully joined {args}".encode(FORMAT))

                elif command == MULTICAST_MESSAGE:
                    try:
                        message = msg.split(maxsplit=2)[2]
                        args = msg.split(maxsplit=2)[1]
                    except:
                        message = None
                        args = None
                    finally:
                        multicast(addr, args, message)
                        conn.send(f"Sent {message} to {args}".encode(FORMAT))

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
            logging("Broadcast", broadcast_message[recieved_messages][0][0], addr[0], broadcast_message[recieved_messages][0][1], addr[1], broadcast_message[recieved_messages][1])
            print("[Server] Message Sent")
            recieved_messages += 1
        
        for x in joined_groups:
            for y in client_groups:
                if x[0] == y[0]:
                    if x[1] < len(y)-1:
                        conn.send(f"{y[x[1]+1][0][1]} {y[x[1]+1][1]} {y[x[1]+1][2]}".encode(FORMAT))
                        logging("Multicast", y[x[1]+1][0][0], addr[0], y[x[1]+1][0][1], addr[1], y[x[1]+1][2])
                        x[1] += 1


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

def join_group(addr, group_name):
    if len(client_groups) == 0:
        client_groups.append([group_name])
    for x in client_groups:
        if group_name not in x:
            client_groups.append([group_name])
    print(f"[{addr[0]}] Joined {group_name}")

def multicast(sender, group_name, message):
    for x in client_groups:
        if group_name in x:
            x.append((sender, group_name, message))
            print(f"{sender} {group_name} {message}")

def logging(name, srcIP, dstIP, srcPort, dstPort, msg):
    if msg == None:
        msglen = 0
    else:
        msglen = len(msg)
    temp = pd.DataFrame({'Type':[name], 'Time(s)':[str(time.time()-starttime)], 'Source_IP':[srcIP], 'Destination_IP':[dstIP], 'Source_Port':[srcPort], 'Destination_Port':[dstPort], 'Length(bytes)':[str(msglen)]})
    global df
    df = pd.concat([df, temp], ignore_index=True)

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
            broadcast(ADDR, args)
        elif command.lower() == JOIN_GROUP:
            print("Invalid command: 'JOIN_GROUP' is not allowed through the console.")
        elif command.lower() == MULTICAST_MESSAGE:
            group_name, message = args.split(maxsplit=1)
            multicast("[Server]", message, group_name)
        elif command == LIST_CLIENT_MESSAGE:
            clients = ""
            for x in client_list:
                clients += f"{x}\n" 
            print(clients, end='')
        else:
            print("Not a valid command")
    df.to_csv('Logging.csv')

print("[Server] Server is starting...")

start()