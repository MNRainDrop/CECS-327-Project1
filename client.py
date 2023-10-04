from globalVariables import *
import socket
import threading

exit_event = threading.Event()

SERVER = "172.22.160.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setblocking(0)
client.settimeout(0.5)
client.connect(ADDR)
print(f"[Client] Connected to {ADDR}")

def send_message():
    connected = True
    while connected:
        if exit_event.is_set():
            connected = False
            client.close()
            break

        print("[Client] Input message to send:")
        msg = input()
        
        message = msg.encode(FORMAT)
        msg_len = len(message)
        send_length = str(msg_len).encode(FORMAT)
        send_length += b' ' * (MESSAGEHEADER - len(send_length))
        try:
            client.send(send_length)
            client.send(message)
        except:
            pass

        if msg.lower() == DISCONNECT_MESSAGE:
            connected = False
            break

def main():
    connected = True
    send = threading.Thread(target=send_message)
    send.start()
    
    while connected:
        try:
            message = client.recv(2048).decode(FORMAT)
            print(message)
            if message == "[Server] Server shut down. You will be disconnected":
                exit_event.set()
                connected = False
                send.join()
        except:
            pass

        if send.is_alive() == False:
            connected = False
    client.close()
main()