from BfresParser.cursor import Cursor
from BfresParser.index_group import search_index_group
from BfresParser.tools import read_string


class Fskl:
    def __init__(self, binary, offset):
        self.binary = binary
        self.offset = offset
        self.header = self.parse_header()

        self.parsed_data = {
            "header": self.header,
            "bones": self.parse_bones()
        }

    def parse_header(self):
        cursor = Cursor(self.binary, self.offset)
        header = {}
        header["magic"] = cursor.read_chars(4)
        header["flags"] = cursor.read_uint32()
        header["bone_count"] = cursor.read_uint16()
        header["smooth_index_count"] = cursor.read_uint16()
        header["rigid_index_count"] = cursor.read_uint16()
        cursor.skip_bytes(2)
        header["bone_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["bones_offset"] = cursor.read_offset()
        header["smooth_index_offset"] = cursor.read_offset()
        header["smooth_matrix_offset"] = cursor.read_offset()
        header["user_pointer"] = cursor.read_uint32()

        return header

    def parse_bones(self):
        bones = []
        for b in self.header["bone_dict"]:
            cursor = Cursor(self.binary, b[1])
            bone = {}
            bone["name"] = read_string(self.binary, cursor.read_offset())
            bone["index"] = cursor.read_uint16()
            bone["parent_index"] = cursor.read_uint16()
            bone["smooth_matrix_index"] = cursor.read_sint16()
            bone["rigid_matrix_index"] = cursor.read_sint16()
            bone["billboard_index"] = cursor.read_sint16()
            bone["user_data_count"] = cursor.read_uint16()
            bone["flags"] = cursor.read_uint32()
            bone["scale"] = [
                cursor.read_float32(),  # X
                cursor.read_float32(),  # Y
                cursor.read_float32()   # Z
            ]
            bone["rotation"] = [
                cursor.read_float32(),  # X
                cursor.read_float32(),  # Y
                cursor.read_float32(),  # Z
                cursor.read_float32()
            ]
            bone["translation"] = [
                cursor.read_float32(),  # X
                cursor.read_float32(),  # Y
                cursor.read_float32()   # Z
            ]
            bone["user_data_dict"] = search_index_group(self.binary, cursor.read_offset())
            bones.append(bone)

        return bones
