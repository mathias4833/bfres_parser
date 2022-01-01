from BfresParser.cursor import Cursor
from BfresParser.tools import read_string
from BfresParser.index_group import search_index_group
from BfresParser.FMDL.fvtx import Fvtx
from BfresParser.FMDL.fmat import Fmat
from BfresParser.FMDL.fskl import Fskl
from BfresParser.FMDL.fshp import Fshp


class Fmdl:
    def __init__(self, binary, bfres_header, offset):
        self.binary = binary
        self.bfres_header = bfres_header
        self.offset = offset
        self.header = self.parse_header()

        self.fvtx_sections = self.parse_fvtx()
        self.fmat_sections = self.parse_fmat()
        self.fskl_section = self.parse_fskl()
        self.fshp_sections = self.parse_fshp()

    def get_parsed_data(self):
        return {
            "header": self.header,
            "fvtx": self.fvtx_sections,
            "fmat": self.fmat_sections,
            "fskl": self.fskl_section,
            "fshp": self.fshp_sections
        }

    def parse_header(self):
        cursor = Cursor(self.binary, self.offset)
        header = {}
        header["magic"] = cursor.read_chars(4)
        header["name"] = read_string(self.binary, cursor.read_offset())
        header["file_path_offset"] = cursor.read_sint32()
        header["fskl_offset"] = cursor.read_offset()
        header["fvtx_array_offset"] = cursor.read_offset()
        header["fshp_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["fmat_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["user_data"] = read_string(self.binary, cursor.read_offset())
        header["fvtx_count"] = cursor.read_uint16()
        header["fshp_count"] = cursor.read_uint16()
        header["fmat_count"] = cursor.read_uint16()
        header["user_data_entry_count"] = cursor.read_uint16()
        header["vertex_count"] = cursor.read_uint32()
        header["user_pointer"] = cursor.read_uint32()

        return header

    def parse_fvtx(self):
        fvtx_sections = []
        for e in range(self.header["fvtx_count"]):
            fvtx_sections.append(Fvtx(self.binary, self.header["fvtx_array_offset"] + e * 0x20).parsed_data)
        return fvtx_sections

    def parse_fmat(self):
        fmat_sections = []
        for section in self.header["fmat_dict"]:
            fmat_sections.append(Fmat(self.binary, self.bfres_header["version"], section[1]).parsed_data)
        return fmat_sections

    def parse_fskl(self):
        return Fskl(self.binary, self.header["fskl_offset"]).parsed_data

    def parse_fshp(self):
        fshp_sections = []
        for section in self.header["fshp_dict"]:
            fshp_sections.append(Fshp(self.binary, section[1]).parsed_data)
        return fshp_sections
