import pickle
import string
import random
from time import sleep
from room import Room


LENGTH_BYTE = 16
ROOM_CODE_LENGTH = 7


def constrain(value: int | float, constraints: list | tuple, overflow=False):
    if value < constraints[0]:
        if overflow:
            value = constraints[1]
        else:
            value = constraints[0]
    elif value > constraints[1]:
        if overflow:
            value = constraints[0]
        else:
            value = constraints[1]
    return value


def sendMessage(connection, message, delay=0):
    sleep(delay)
    encoded = pickle.dumps(message)
    connection.send(pickle.dumps(len(encoded)))
    connection.send(encoded)


def recvMessage(connection):
    msgLength = pickle.loads(connection.recv(LENGTH_BYTE))
    msg = pickle.loads(connection.recv(msgLength))
    return msg


def generate_room_code():
    code = ''.join(random.choices(list(string.ascii_lowercase), k=ROOM_CODE_LENGTH))
    while code in Room.rooms.keys():
        code = ''.join(random.choices(list(string.ascii_lowercase), k=ROOM_CODE_LENGTH))
    return code


def mode_to_string(mode):
    return str(mode[0]) + str(mode[1])


def log(text, after_text=''):
    print(f'[{text}] {after_text}')
