import socket
import pickle


HOST = "192.168.0.12"
PORT = 7070
LENGTH_BYTE = 1024
ADDRESS = (HOST, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(ADDRESS)
    online = True
except ConnectionRefusedError:
    online = False


def sendMessage(message):
    encoded = pickle.dumps(message)
    client.send(pickle.dumps(len(encoded)))
    client.send(encoded)
    print('sent')


def recvMessage():
    length = pickle.loads(client.recv(LENGTH_BYTE))
    value = pickle.loads(client.recv(length))
    return value


def joinRoom(roomCode):
    sendMessage(("join", roomCode))
    msg = recvMessage()
    return msg


def createRoom(roomCode):
    sendMessage(("create", roomCode))
    msg = recvMessage()
    return msg


def leaveRoom():
    sendMessage(("leave",))
    msg = recvMessage()
    return msg


def disconnect():
    sendMessage(("disconnected",))
    msg = recvMessage()
    return msg


def updateOpponent():
    sendMessage(('getOpponentSnake',))
    msg = recvMessage()
    print('msg')
    return msg


def sendSnakeData(snake):
    sendMessage(('snakeData', snake))


def isOpponentConnected():
    sendMessage(('isOpponentConnected',))
    msg = recvMessage()
    return msg
