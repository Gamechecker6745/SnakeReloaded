import pickle
import string
import random
import struct
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
    packet = pickle.dumps(message)
    length = struct.pack('!I', len(packet))
    packet = length + packet
    connection.send(packet)


def recvMessage(connection):
    buf = b''
    while len(buf) < 4:
        buf += connection.recv(4 - len(buf))

    length = struct.unpack('!I', buf)[0]

    rawMessage = connection.recv(length)
    msg = pickle.loads(rawMessage)
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
