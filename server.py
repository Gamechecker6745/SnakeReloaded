import socket
import threading
import pickle
import classes as cls


def sendMessage(connection, message):
    encoded = pickle.dumps(message)
    connection.send(pickle.dumps(len(encoded)))
    connection.send(encoded)
    print(f"[MESSAGE SENT] {message}")


def recvMessage(connection, lengthByte):
    msgLength = pickle.loads(connection.recv(lengthByte))
    msg = pickle.loads(connection.recv(msgLength))
    return msg


class Client:
    Rooms = {}

    def __init__(self, connection: socket.socket, address, start=True, LENGTH_BYTE=100):
        self.snake = cls.Snake()
        self.connected = True
        self.game_id: None | str = None
        self.host: None | bool = None
        self.opponent: Client = None
        if start:
            self.address = address
            self.connection: socket.socket = connection
            self.handleClientMessages(LENGTH_BYTE)

    def handleClientMessages(self, LENGTH_BYTE):
        while self.connected:
            msg = recvMessage(self.connection, LENGTH_BYTE)
            print(f"\n[MESSAGE] - {self.address}: {msg}")

            if msg[0] == 'disconnected':
                self.disconnect()

            elif msg[0] == 'create':
                self.createRoom(msg[1])

            elif msg[0] == 'join':
                self.joinRoom(msg[1])

            elif msg[0] == 'snakeData':
                self.updateSnake(msg[1])

            elif msg[0] == 'leave':
                self.leaveRoom()

            elif msg[0] == 'isOpponentConnected':
                self.opponentIsConnected()

            elif msg[0] == 'getOpponentSnake':
                self.getOpponentSnake()

    def createRoom(self, roomCode):
        if roomCode not in Client.Rooms.keys():
            Client.Rooms[roomCode] = [self]
            self.game_id = roomCode
            self.host = True
            sendMessage(self.connection, "Room created!")
        else:
            sendMessage(self.connection, "Invalid Room #")

    def joinRoom(self, roomCode):
        error = None
        if roomCode not in Client.Rooms:
            error = 'Invalid room #'
        elif len(Client.Rooms[roomCode]) > 1:
            error = 'Room full'

        if error is None:
            Client.Rooms[roomCode].append(self)
            self.opponent = Client.Rooms[roomCode][0]
            self.opponent.opponent = self
            self.game_id = roomCode
            self.host = False
            sendMessage(self.connection, "Joining room")
        else:
            sendMessage(self.connection, error)

    def leaveRoom(self):
        if self.game_id is not None:
            del Client.Rooms[self.game_id]
            if self.opponent is not None:
                self.opponent.__init__(self.opponent.connection, self.opponent.address, False)
            self.__init__(self.connection, self.address, False)
        sendMessage(self.connection, "Room left")

    def updateSnake(self, snake):
        self.snake = snake

    def opponentIsConnected(self):
        sendMessage(self.connection, self.opponent is not None)

    def getOpponentSnake(self):
        sendMessage(self.connection, self.opponent.snake)

    def disconnect(self):
        if self.game_id is not None:
            self.leaveRoom()
        self.connected = False
        sendMessage(self.connection, "Disconnected")
        self.connection.close()
        del self


def main():
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 7070
    ADDRESS = (HOST, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDRESS)

    print("[SERVER STARTING]")
    print(f"[STARTED] Server running on {HOST}")

    def acceptConnections():
        server.listen()
        while True:
            connection, address = server.accept()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            thread = threading.Thread(target=Client, args=(connection, address))
            thread.start()

    acceptConnections()


if __name__ == '__main__':
    main()
