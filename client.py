from globalVariables import *
import socket

SERVER = "172.22.160.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"[Client] Connected to {ADDR}")

def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b' ' * (MESSAGEHEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def main():
    connected = True
    while connected:
        print("[Client] Input message to send:\n")
        msg = input()
        send(msg)
        if msg == DISCONNECT_MESSAGE:
            connected = False
            client.close()
main()