from BfresParser.cursor import Cursor
from BfresParser.tools import read_string


def search_index_group(binary, offset):
    if offset == 0:
        return 0
    cursor = Cursor(binary, offset)
    cursor.skip_bytes(4)
    count = cursor.read_sint32()
    cursor.skip_bytes(24)
    targets = []
    for e in range(count):
        name_pointer = cursor.read_offset()
        name = ""
        if name_pointer > 0:
            name = read_string(binary, name_pointer)

        data_pointer = cursor.read_offset()
        targets.append([name, data_pointer])
        cursor.skip_bytes(8)
    return targets
