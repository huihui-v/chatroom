import socket
import sys
import json

f = open("config.json", 'r')
setting = json.load(f)
host = setting['host']
port = int(setting['port'])

def connectSocket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'FAILED to create socket. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'Socket Created'
    return s;

def test():
    socket = connectSocket();
    string = 'teststring';
    try:
        socket.connect((host, port))
        s.send(string)
    except socket.error, msg:
        print 'FAILED to create socket. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'msg sent'

test();
