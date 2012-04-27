import struct
import sys
from dota import demo_pb2

class DemoHeader(object):
    def __init__(self, filestamp, fileinfo_offset):
        assert filestamp == 'PBUFDEM\0'
        self.filestamp = filestamp
        self.fileinfo_offset = fileinfo_offset

def read_var_int_32(f):
    count = 0
    result = 0
    while True:
        if (count == 5):
            return result
        b = struct.unpack('B', f.read(1))[0]
        result = result | (b & 0x7F) << (7 * count)
        count += 1
        if not b & 0x80:
            break
    return result


def read_header(f):
    header = DemoHeader(f.read(8), f.read(4))
    print header.filestamp
    print header.fileinfo_offset
    return header

def read_message_type(f):
    cmd = read_var_int_32(f)
    tick = read_var_int_32(f)
    return tick, cmd

with open(sys.argv[1], 'rb') as f:
    header = DemoHeader(f.read(8), f.read(4))
    tick, cmd = read_message_type(f)
    print tick, cmd

    #demo = demo_pb2.CDemoFileHeader()
    #demo.ParseFromString(f.read())

    # Read int32
    # Switch based on that to find message
    # Process message