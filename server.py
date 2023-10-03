import socket
import threading
from globalVariables import *
import os

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# creates socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[Server] Socket Created")

# bind to the port
server.bind(ADDR)
print(f"[Server] Server bound to {ADDR}")

def handle_client(conn, addr):
    print(os.getpid())
    print(f"[Server] New connection : {addr}")

    connected = True
    while connected:
        msg_len = conn.recv(MESSAGEHEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
    conn.close()

def start():
    # listen for connections
    server.listen()
    print(f"[Server] Server is listening on {SERVER}")
    while True:
        # when connection is established create a new thread of handle_client
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[Server] Active Connections {threading.active_count() - 1}")

print("[Server] Server is starting...")
start()