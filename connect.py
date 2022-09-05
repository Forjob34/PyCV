import socket
from msg_create import string_b, upload_msg, del_msg, load_msg, msg


sock = socket.socket()

sock.connect(('192.168.0.2', 29043))
sock.setblocking(0)

try:
    sock.send(msg.decode('unicode_escape').encode('raw_unicode_escape'))
    sock.settimeout(30)
except Exception as e:
    print(e)
# sock.send(del_msg)
# sock.settimeout(30)
# sock.send(upload_msg)
# sock.settimeout(30)
sock.send(load_msg)
sock.settimeout(30)

try:
    data = sock.recv(65536)
    response = data.decode('utf-8', 'replace')
except socket.error:
    print('No DATA')
    sock.close()
else:
    print(f'Server answer {data}')
    # print(f'Server answer {response}')
    with open('answers.txt', 'a+') as file:
        file.write(str(data) + '\n')
        file.write('\n')
    sock.close()
