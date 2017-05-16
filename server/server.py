import socket
import sys
import json
import threading
f = open("config.json", 'r+b')
setting = json.load(f)
host = setting['host']
port = int(setting['port'])
cons = []
addrs = []
info = {"status": "", "info": "", "targetip": "", "sourceip": "", "sourceport": "", "body": ""}

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
    new_info['status'] = "RECV"
    new_info['info'] = msg['info']
    new_info['targetip'] = msg['targetip']
    new_info['sourceip'] = sourceip
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def send_info(conn, res):
    new_info = info
    new_info['status'] = "RESP"
    new_info['body'] = res;
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def reply_disconnect_confirm(conn):
    new_info = info
    new_info['status'] = "DISCONNECT_OK"
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def reply_ok(conn):
    new_info = info
    new_info['status'] = "SENT_OK"
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def reply_offline(conn):
    new_info = info
    new_info['status'] = "OFFLINE"
    in_json = json.dumps(new_info)
    conn.sendall(in_json)

def push_notification(conn, addr, status):
    new_info = info
    new_info['status'] = status
    new_info['sourceip'] = addr[0]
    new_info['sourceport'] = addr[1]
    in_json = json.dumps(new_info)
    conn.sendall(in_json)


def handle_connection(conn, addr):
    for i in range(0, len(cons)):
        push_notification(cons[i], addr, "LOGIN");
    cons.append(conn)
    addrs.append(addr)
    print addr[0] + ':' + str(addr[1]) + ' connected!'
    while 1:
        recv_info = conn.recv(1024)
        recv_info = json.loads(recv_info)
        if recv_info['status'] == 'SEND':
            flag = 0
            print 'From '+ addr[0]+ ' to '+ recv_info['targetip']+ ':'
            print recv_info['info']
            for i in range(0, len(addrs)):
                if addrs[i][0] == recv_info['targetip']:
                    send_msg(cons[i], addr[0], recv_info);
                    reply_ok(conn);
                    flag = 1
                    break;
            if flag == 0:
                reply_offline(conn);

        elif recv_info['status'] == "GET":
            if recv_info['body'] == "get_user_list":
                res = []
                for i in range(0, len(addrs)):
                    res.append(addrs[i]);
                send_info(conn, res)

        elif recv_info['status'] == 'DISCONNECT':
            for i in range(0, len(addrs)):
                if addrs[i][0] == addr[0]:
                    addrs.remove(addrs[i])
                    cons.remove(cons[i])
                    for i in range(0, len(cons)):
                        push_notification(cons[i], addr, "LOGOUT")
                    print addr[0]+ ":"+ str(addr[1])+ " disconnected"
                    reply_disconnect_confirm(conn)
                    break;
            conn.close()
            return;

        continue;
    return;

def index():
    s = bind_socket()
    while 1:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_connection, args=(conn, addr,))
        thread.start()

index();
