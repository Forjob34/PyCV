import socket


def add_hex(message, hex_string):
    if isinstance(message, bytes):
        message = message.hex()
        return bytes.fromhex(message + hex_string)

    return bytes.fromhex(message + hex_string)


def calc_checksum(message):
    checksum = 0

    if isinstance(message, bytes):
        message = message.hex(' ')
    else:
        return 'message must be a byte string'
    hex_list = message.split(' ')

    for i in hex_list:
        if '1b' in i:
            continue
        dec = int(i, 16)
        checksum = dec + checksum

    if len(str(checksum)) >= 3:
        checksum = hex(checksum).replace('0x', '')
        checksum = int((str(checksum)[1:]), 16)

    checksum = hex(256 - checksum).replace('0x', '')
    message = message.replace(' ', '') + checksum

    return bytes.fromhex(message)


sock = socket.socket()

sock.connect(('192.168.0.2', 29043))
sock.setblocking(0)

message = add_hex('', '1b02')  # ;ESC STX Sequence
message = add_hex(message, '18')  # ;Command ID - Raster Data Request
message = add_hex(message, '1b03')  # ;ESC ETX sequence
message = add_hex(message, 'e3')  # ;Checksum

sock.send(message)
sock.settimeout(30)

try:
    data = sock.recv(65536)
    # response = data.decode('ascii', 'replace')
except socket.error:
    print('No DATA')
    sock.close()
else:
    print(f'Server answer {data}')
    sock.close()
