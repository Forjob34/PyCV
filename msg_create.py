from asyncio import SendfileNotAvailableError
import re
import json


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

    ch_list = []

    for i in hex_list:
        if '1b' in i:
            ch_list.append(i)
            continue
        dec = int(i, 16)
        checksum = dec + checksum

    message = message.replace(' ', '')

    if len(ch_list) > 2:
        if '1b1b' in message:
            checksum = checksum + 27
    # print(checksum)
    if len(hex(checksum).replace('0x', '')) == 3:
        checksum = hex(checksum).replace('0x', '')
        checksum = int((str(checksum)[1:]), 16)
    if len(hex(checksum).replace('0x', '')) == 4:
        checksum = hex(checksum).replace('0x', '')
        checksum = int((str(checksum)[2:]), 16)

    checksum = hex(256 - checksum).replace('0x', '')

    if len(checksum) == 1:
        checksum = '0' + str(checksum)
    print(checksum)

    message = message + checksum

    return message


def data_from_json(path_to_json):
    with open(path_to_json, 'r') as file:
        templates = json.load(file)

    rad_height = int(templates['radiator_type']['sizes']['height'])
    rad_lenght = int(templates['radiator_type']['sizes']['lenght'])

    hex_height = ''
    hex_lenght = ''
    for i in str(rad_height):
        hex_height += hex(ord(i)).replace('0x', '')
    for i in str(rad_lenght):
        hex_lenght += hex(ord(i)).replace('0x', '')

    return hex_height, hex_lenght

# +++++++++++++++++++++++++ Variables ++++++++++++++++++++++++++++++++


standart_msg_len = 'c6'  # 4b + 20 + 32 (text, time, date)
rad_sizes_len = hex((len(data_from_json('sizes.json')[
    0] + data_from_json('sizes.json')[1]) // 2) + 52).replace('0x', '')
print(rad_sizes_len)


def calc_rast_lenght(rad_sizes_len):
    rad_rastr_len = hex(107).replace('0x', '')  # default = 3b

    if rad_sizes_len == hex(58).replace('0x', ''):
        return rad_rastr_len
    elif rad_sizes_len == hex(59).replace('0x', ''):
        rad_rastr_len = hex(113).replace('0x', '')
        return rad_rastr_len
    elif rad_sizes_len == hex(60).replace('0x', ''):
        rad_rastr_len = hex(119).replace('0x', '')
        return rad_rastr_len


def calc_str_lenght():
    rad_str_len = hex(14 + 5 + int(len((data_from_json('sizes.json')
                                        [0] + data_from_json('sizes.json')[1])) // 2)).replace('0x', '')
    if rad_str_len == '1b':
        return '1b1b'
    else:
        return rad_str_len


def calc_msg_lenght(standart_msg_len, rad_sizes_len):
    total_msg_len = hex(int(standart_msg_len, 16) +
                        int(rad_sizes_len, 16)).replace('0x', '')
    print(total_msg_len)
    if len(str(total_msg_len)) > 2:
        total_msg_len = str(total_msg_len + '0')
        total_msg_len = total_msg_len[::-1]
        print(total_msg_len)

    return total_msg_len


# +++++++++++++++++ Download Message on printer ++++++++++++++++++++++
message = add_hex('', '1b021901')  # command and msg ID
# lenght in bytes
message = add_hex(
    message, f'{calc_msg_lenght(standart_msg_len, rad_sizes_len)}')
message = add_hex(message, 'fb000666000000')  # lenght in raster and etc
message = add_hex(message, '4F4E450000000000')  # Msg NAME (ONE)
message = add_hex(message, '0000000000000000')
message = add_hex(message, '323120535444204C')  # Raster Name (21 STD LIN)
message = add_hex(message, '494E000000000000')
message = add_hex(message, '1c004b00000000fb000c00012a000000')
message = add_hex(message, '313220464820554E')  # ;Data set name 12 FH UNI
message = add_hex(message, '4900000000000000')
message = add_hex(message, 'D0A4D0BED180D182D0B520')  # Forte
message = add_hex(message, 'D09FD180D0BED0BC20')  # Prom
message = add_hex(message, 'D0A1D182D0B8D0BB20')  # Still
message = add_hex(message, 'D093D0BCD0B1D0A520')  # GmbH
message = add_hex(message, '3230323200')  # 2022
message = add_hex(message, '1c0220000e00001d0007000105000000')  # Time header
message = add_hex(message, '3720464820554E49')  # ;Data set name 7 FH UNI
message = add_hex(message, '0000000000000000')
message = add_hex(message, '1c0532000e28003b0007000110000000')  # Date header
message = add_hex(message, '3720464820554E49')  # ;Data set name 7 FH UNI
message = add_hex(message, '0000000000000000')
message = add_hex(message, '276464272E274D4D')  # DAte message
message = add_hex(message, '272E277979270000')
message = add_hex(message, '0000')
message = add_hex(message, '1c00')  # TExt header
message = add_hex(message, str(rad_sizes_len))  # text lenght
message = add_hex(
    message, f'000e7200{calc_rast_lenght(rad_sizes_len)}00070001{calc_str_lenght()}000000')  # TExt header
message = add_hex(message, '3720464820554E49')  # ;Data set name 7 FH UNI
message = add_hex(message, '0000000000000000')
message = add_hex(message, '31312D')  # 11-
message = add_hex(message, data_from_json('sizes.json')[0])  # 500
message = add_hex(message, '2d')  # -
message = add_hex(message, data_from_json('sizes.json')[1])  # 800
message = add_hex(message, '20')
message = add_hex(message, 'D091D0BED0BAD0BED0B2D0BED0B500')  # msg Bokovoe
message = add_hex(message, '1b03')
message = calc_checksum(message)
# print(message)

# +++++++++++++++++++ Data directory +++++++++++++++++++++
# message = add_hex('', '1b0261431b03')
# message = calc_checksum(message)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++ Del message ++++++++++++++++++++++++
# message = add_hex('', '1b021b1b01')
# message = add_hex(message, '4F4E450000000000')
# message = add_hex(message, '0000000000000000')
# message = add_hex(message, '1b03')
# message = calc_checksum(message)
# print(message)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++ Load msg on disp ++++++++++++++++++++++++++
# message = add_hex('', '1b021e')
# message = add_hex(message, '4F4E450000000000')
# message = add_hex(message, '0000000000000000')
# message = add_hex(message, '0000')
# message = add_hex(message, '1b03')
# message = calc_checksum(message)
# print(message)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++ Upload Msg +++++++++++++++++++++++++++++++++
# message = add_hex('', '1b021a01')
# message = add_hex(message, '4F4E450000000000')
# message = add_hex(message, '0000000000000000')
# # message = add_hex(message, '0000')
# message = add_hex(message, '1b03')
# message = calc_checksum(message)
# print(message)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++


# msg = b'\x1b\x02\x19\x01\x00\x01\xfb\x00\x06\x66\x00\x00\x00\x4f\x4e\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x32\x31\x20\x53\x54\x44\x20\x4c\x49\x4e\x00\x00\x00\x00\x00\x00\x1c\x00\x4b\x00\x00\x00\x00\xfb\x00\x0c\x00\x01\x2a\x00\x00\x00\x31\x32\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\xd0\xa4\xd0\xbe\xd1\x80\xd1\x82\xd0\xb5\x20\xd0\x9f\xd1\x80\xd0\xbe\xd0\xbc\x20\xd0\xa1\xd1\x82\xd0\xb8\xd0\xbb\x20\xd0\x93\xd0\xbc\xd0\xb1\xd0\xa5\x20\x32\x30\x32\x32\x00\x1c\x02\x20\x00\x0e\x00\x00\x1d\x00\x07\x00\x01\x05\x00\x00\x00\x37\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x05\x32\x00\x0e\x28\x00\x3b\x00\x07\x00\x01\x10\x00\x00\x00\x37\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\x00\x27\x64\x64\x27\x2e\x27\x4d\x4d\x27\x2e\x27\x79\x79\x27\x00\x00\x00\x00\x1c\x00\x3a\x00\x0e\x72\x00\x6b\x00\x07\x00\x01\x19\x00\x00\x00\x37\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\x00\x31\x31\x2d\x35\x30\x30\x2d\x37\x30\x30\x20\xd0\x91\xd0\xbe\xd0\xba\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb5\x00\x1b\x03\xa4'
# msg = b'\x1b\x02\x19\x01\x00\x01\xfb\x00\x06\x66\x00\x00\x00\x4f\x4e\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x32\x31\x20\x53\x54\x44\x20\x4c\x49\x4e\x00\x00\x00\x00\x00\x00\x1c\x00\x4b\x00\x00\x00\x00\xfb\x00\x0c\x00\x01\x2a\x00\x00\x00\x31\x32\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\xd0\xa4\xd0\xbe\xd1\x80\xd1\x82\xd0\xb5\x20\xd0\x9f\xd1\x80\xd0\xbe\xd0\xbc\x20\xd0\xa1\xd1\x82\xd0\xb8\xd0\xbb\x20\xd0\x93\xd0\xbc\xd0\xb1\xd0\xa5\x20\x32\x30\x32\x32\x00\x1c\x02\x20\x00\x0e\x00\x00\x1d\x00\x07\x00\x01\x05\x00\x00\x00\x37\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x05\x32\x00\x0e\x28\x00\x3b\x00\x07\x00\x01\x10\x00\x00\x00\x37\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\x00\x27\x64\x64\x27\x2e\x27\x4d\x4d\x27\x2e\x27\x79\x79\x27\x00\x00\x00\x00\x1c\x00\x3a\x00\x0e\x72\x00\x6b\x00\x07\x00\x01\x19\x00\x00\x00\x37\x20\x46\x48\x20\x55\x4e\x49\x00\x00\x00\x00\x00\x00\x00\x00\x31\x31\x2d\x35\x30\x30\x2d\x35\x30\x30\x20\xd0\x91\xd0\xbe\xd0\xba\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb5\x00\x1b\x03\xa6'
load_msg = b'\x1b\x02\x1e\x4f\x4e\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b\x03\xfb'
del_msg = b'\x1b\x02\x1b\x1b\x01\x4f\x4e\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b\x03\xfd'
upload_msg = b'\x1b\x02\x1a\x01\x4f\x4e\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b\x03\xfe'
check_status = b'\x1b\x02\x14\x1b\x03\xe7'
raster_data_req = b'\x1b\x02\x18\x1b\x03\xe3'
char_data_req = b'\x1b\x02\x61\x43\x1b\x03\x57'

byte_str = [f'\\x{i}' for i in re.findall(r'\w{2}', message)]
string_b = ''.join(byte_str)
msg = bytes(string_b, 'utf-8')
