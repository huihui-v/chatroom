import socket
import sys
import json
import threading
f = open("config.json", 'r')
setting = json.load(f)
host = setting['host']
port = int(setting['port'])
info = {"status": "", "info": "", "targetip": "", "body": ""}

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'FAILED to create socket. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'Socket Created'
    return s;

def connect_to_server():
    s = create_socket();
    try:
        s.connect((host, port))
    except socket.error, msg:
        print 'FAILED to create connection. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
        sys.exit()
    print 'Connection created! Please input your command'
    return s;

def input_command ():
    string = raw_input()
    return str(string).split(' ');

def disconnect(s):
    new_info = info;
    new_info['status'] = "DISCONNECT"
    in_json = json.dumps(new_info);
    s.sendall(in_json)

def send_msg(target, msg, s):
    new_info = info;
    new_info['status'] = "SEND"
    new_info['targetip'] = target
    new_info['info'] = msg
    in_json = json.dumps(new_info);
    s.sendall(in_json)

def send_request(s, req):
    new_info = info;
    new_info['status'] = "GET"
    new_info['body'] = req
    in_json = json.dumps(new_info)
    s.sendall(in_json)

def listen (s):
    while 1:
        recv_info = s.recv(1024)
        recv_info = json.loads(recv_info);
        if recv_info['status'] == 'RECV':
            print 'Receive from ', recv_info['sourceip'], ':'
            print recv_info['info']
            continue;
        elif recv_info['status'] == 'RESP':
            for i in range(0, len(recv_info['body'])):
                print recv_info['body'][i][0]+":"+str(recv_info['body'][i][1])
            continue;
        elif recv_info['status'] == 'SENT_OK':
            print 'Message sent!'
            continue;
        elif recv_info['status'] == 'OFFLINE':
            print 'Error: Receiver Offline!'
            continue;
        elif recv_info['status'] == 'LOGIN':
            print recv_info['sourceip']+":"+str(recv_info['sourceport'])+" logged in!"
            continue;
        elif recv_info['status'] == 'LOGOUT':
            print recv_info['sourceip']+":"+str(recv_info['sourceport'])+" logged out!"
            continue;
        elif recv_info['status'] == 'DISCONNECT_OK':
            s.close()
            print 'Disconnected!'
            break;
        else:
            print recv_info
            continue;
    return;

def index ():
    s = connect_to_server()
    thread = threading.Thread(target=listen,args=(s,))
    thread.start()
    while(1):
        command = input_command()
        if (command[0] == 'quit'):
            disconnect(s);
            break;
        elif (command[0] == 'list'):
            send_request(s, 'get_user_list')
            continue;
        elif (command[0] == 'send'):
            try:
                send_msg(command[1], command[2], s)
                continue;
            except Exception, e:
                print Exception, ":", e
    return;

index();
