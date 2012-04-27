import cStringIO as StringIO
import struct
import sys
from dota import demo_pb2
from dota import netmessages_pb2

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
    return header

def read_message_type(f, compressed):
    cmd = read_var_int_32(f)
    tick = read_var_int_32(f)
    if compressed:
        compressed = not not (cmd & demo_pb2.DEM_IsCompressed)
    cmd = (cmd & ~demo_pb2.DEM_IsCompressed)
    return tick, cmd, compressed

def read_message(f, cls):
    # TODO: Compression handling
    size = read_var_int_32(f)
    uncompressed_size = size
    message = cls()
    message.ParseFromString(f.read(size))
    return message, size, uncompressed_size

def print_demo_header(message, tick, frame, size, uncompressed_size):
	print "==== #{frame}: Tick:{tick} '{command_name}' Size:{size} UncompressedSize:{uncompressed_size} ====".format(
        frame=frame,
        tick=tick,
        command_name=repr(type(message)),
        size=size,
        uncompressed_size=size
    )

def print_demo_string_table(message):
    # TODO: String table
    print message

def print_message(message, tick, frame, size, uncompressed_size):
    print_demo_header(message, tick, frame, size, uncompressed_size)
    print_demo_string_table(message)

def build_command_list(module, command_prefix, class_prefix):
    commands = {}
    for attr in [a for a in dir(module) if a.startswith(command_prefix)]:
        classname = attr.replace(command_prefix, class_prefix)
        try:
            commands[getattr(module, attr)] = getattr(module, classname)
            print getattr(module, attr), '->', classname
        except AttributeError:
            print 'missing:', attr, classname
    return commands


if __name__ == "__main__":
    commands = {}
    commands.update(build_command_list(demo_pb2, 'DEM_', 'CDemo'))
    commands.update({8: demo_pb2.CDemoPacket})
    commands.update(build_command_list(netmessages_pb2, 'DEM_', 'CNETMsg'))

    with open(sys.argv[1], 'rb') as f:
        buff = StringIO.StringIO(f.read())

    compressed = False
    header = DemoHeader(buff.read(8), buff.read(4))
    print header.filestamp
    print header.fileinfo_offset

    frame = 0
    messages = []
    while True:
        tick, cmd, compressed = read_message_type(buff, compressed)
        print tick, cmd, compressed
        cls = commands[cmd]
        message, size, uncompressed_size = read_message(buff, cls)
        print_message(message, tick, frame, size, uncompressed_size)

        frame += 1

