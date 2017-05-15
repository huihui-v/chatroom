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
    s = connectSocket();
    string = "";
    try:
        s.bind((host, port))
        s.listen(10)
        print 'socket now listening'
        conn, addr = s.accept()
        print 'connected with ' + addr[0] + ':' + str(addr[1])

        srting = conn.recv()
        print string;
        
    except socket.error, msg:
        print 'FAILED to bind port. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'msg received'
    print string;

test();
