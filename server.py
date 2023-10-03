import socket

# creates socket object
s = socket.socket()
print("Socket successfully created")

# reserve port
port = 8080

# bind to the port
s.bind(('', port))
print("Socket binded to %s" %(port))

# listen
s.listen(5)
print("Socket is listening")

while True:
    c, addr = s.accept()
    print("Got connection from", addr)

    c.send("Thank you for connecting".encode())

    c.close()

    break