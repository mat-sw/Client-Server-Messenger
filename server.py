import socket
import threading

HOST = '127.0.0.1'
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

list_of_clients = []
nicknames = []


# broadcast - send message to all the connected clients
def broadcast(msg):
    for client in list_of_clients:
        client.send(msg)


# handle - handle the individual connections to the clients
def handle(client):
    while True:
        try:
            msg = client.recv(1024)
            print(f"{nicknames[list_of_clients.index(client)]} : {msg}")
            broadcast(msg)
        except:
            index = list_of_clients.index(client)
            list_of_clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


# receive - listen and accept new connections
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with: {str(address)}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)
        nicknames.append(nickname)
        list_of_clients.append(client)

        print(f"Client's nickname is: {nickname}")
        broadcast(f"{nickname} joined\n".encode('utf-8'))
        client.send("Connected to the server".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


try:
    receive()
except KeyboardInterrupt:
    exit