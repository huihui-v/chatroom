import socket
import sys
import json
import threading
f = open("config.json", 'r')
setting = json.load(f)
host = setting['host']
port = int(setting['port'])
cons = []
addrs = []
info = {"status": "", "info": "", "targetip": "", "sourceip": ""}

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'FAILED to create socket. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'Socket Created'
    return s;

def bind_socket():
    s = create_socket();
    try:
        s.bind((host, port))
        s.listen(10)
    except socket.error, msg:
        print 'FAILED to bind port. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'socket now listening'
    return s;

def send_msg(conn, sourceip, msg):
    new_info = info
    new_info['status'] = "SEND"
    new_info['info'] = msg['info']
    new_info['targetip'] = msg['targetip']
    new_info['sourceip'] = sourceip
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def reply_ok(conn):
    new_info = info
    new_info['status'] = "OK"
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def reply_offline(conn):
    new_info = info
    new_info['status'] = "OFFLINE"
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def handle_connection(conn, addr):
    cons.append(conn)
    addrs.append(addr)
    print 'connected with ' + addr[0] + ':' + str(addr[1])
    while 1:
        recv_info = conn.recv(1024)
        recv_info = json.loads(recv_info)
        if recv_info['status'] == 'SEND':
            flag = 0
            for i in addrs:
                if addrs[i][0] == recv_info['targetip']:
                    send_msg(cons[i], addr[0], recv_info);
                    print 'From ', addr[0], ' to ', recv_info['targetip'], ':'
                    print recv_info['info']
                    flag = 1
                    reply_ok(conn);
                    break;
            if flag == 0:
                reply_offline(conn);
        elif recv_info['status'] == 'DISCONNECT':
            for i in addrs:
                if addrs[i][0] == addr[0]:
                    addrs.remove(i)
                    cons.remove(i)
                    print addr[0], " disconnected"
                    break;
            conn.close()
            break;
    return;

def index():
    s = bind_socket()
    while 1:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_connection, args=(conn, addr))
        thread.start()

index();
