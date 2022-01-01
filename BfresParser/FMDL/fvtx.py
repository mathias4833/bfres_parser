from BfresParser.cursor import Cursor
from BfresParser.index_group import search_index_group
from BfresParser.tools import read_string


class Fvtx:
    def __init__(self, binary, offset):
        self.binary = binary
        self.offset = offset
        self.header = self.parse_header()

        self.parsed_data = {
            "header": self.header,
            "attributes": self.parse_fvtx()
        }

    def parse_header(self):
        cursor = Cursor(self.binary, self.offset)
        data = {}
        data["magic"] = cursor.read_chars(4)
        data["attribute_count"] = cursor.read_uint8()
        data["buffer_count"] = cursor.read_uint8()
        data["section_index"] = cursor.read_uint16()
        data["vertex_count"] = cursor.read_uint32()
        data["vertex_skin_count"] = cursor.read_uint8()
        cursor.skip_bytes(3)
        data["attribute_array_offset"] = cursor.read_offset()
        data["attributes_dict"] = search_index_group(self.binary, cursor.read_offset())
        data["buffer_array_offset"] = cursor.read_offset()
        data["user_pointer"] = cursor.read_uint32()

        return data

    def parse_attribute(self, offset):
        attr_cursor = Cursor(self.binary, offset)
        attr = {}
        name = read_string(self.binary, attr_cursor.read_offset())
        attr["buffer_index"] = attr_cursor.read_uint8()
        attr_cursor.skip_bytes()
        attr["buffer_offset"] = attr_cursor.read_uint16()
        attr["format"] = attr_cursor.read_uint32()

        buff_cursor = Cursor(self.binary, self.header["buffer_array_offset"] + attr["buffer_index"] * 0x18)
        buff_header = {
            "data_pointer": buff_cursor.read_uint32(),
            "size": buff_cursor.read_uint32(),
            "handle": buff_cursor.read_uint32(),
            "stride": buff_cursor.read_uint16(),
            "buffering_count": buff_cursor.read_uint16(),
            "context_pointer": buff_cursor.read_uint32(),
            "data_offset": buff_cursor.read_offset()
        }

        vertices = []
        for v in range(self.header["vertex_count"]):
            buff_cursor.go_to(attr["buffer_offset"] + buff_header["data_offset"] + v * buff_header["stride"])
            if attr["format"] == 0x0000:
                attr["format_name"] = "unorm_8"
                vertices.append([float(buff_cursor.read_uint8()) / 255])
            elif attr["format"] == 0x0004:
                attr["format_name"] = "unorm_8_8"
                vertices.append([
                    float(buff_cursor.read_uint8()) / 255,
                    float(buff_cursor.read_uint8()) / 255
                ])
            elif attr["format"] == 0x0007:
                attr["format_name"] = "unorm_16_16"
                vertices.append([
                    float(buff_cursor.read_uint16()) / 65535,
                    float(buff_cursor.read_uint16()) / 65535
                ])
            elif attr["format"] == 0x000A:
                attr["format_name"] = "unorm_8_8_8_8"
                vertices.append([
                    buff_cursor.read_uint8() / 255,
                    buff_cursor.read_uint8() / 255,
                    buff_cursor.read_uint8() / 255,
                    buff_cursor.read_uint8() / 255
                ])
            elif attr["format"] == 0x0100:
                attr["format_name"] = "uint_8"
                vertices.append([
                    int(buff_cursor.read_uint8()),
                ])
            elif attr["format"] == 0x0104:
                attr["format_name"] = "uint_8_8"
                vertices.append([
                    int(buff_cursor.read_uint8()),
                    int(buff_cursor.read_uint8())
                ])
            elif attr["format"] == 0x010A:
                attr["format_name"] = "uint_8_8_8_8"
                vertices.append([
                    int(buff_cursor.read_uint8()),
                    int(buff_cursor.read_uint8()),
                    int(buff_cursor.read_uint8()),
                    int(buff_cursor.read_uint8())
                ])
            elif attr["format"] == 0x0200:
                attr["format_name"] = "snorm_8"
                vertices.append([
                    float(buff_cursor.read_sint8()) / 127
                ])
            elif attr["format"] == 0x0204:
                attr["format_name"] = "snorm_8_8"
                vertices.append([
                    float(buff_cursor.read_sint8()) / 127,
                    float(buff_cursor.read_sint8()) / 127
                ])
            elif attr["format"] == 0x0207:
                attr["format_name"] = "snorm_16_16"
                vertices.append([
                    float(buff_cursor.read_sint16()) / 32767,
                    float(buff_cursor.read_sint16()) / 32767
                ])
            elif attr["format"] == 0x020A:
                attr["format_name"] = "snorm_8_8_8_8"
                vertices.append([
                    float(buff_cursor.read_sint8()) / 127,
                    float(buff_cursor.read_sint8()) / 127,
                    float(buff_cursor.read_sint8()) / 127,
                    float(buff_cursor.read_sint8()) / 127
                ])
            elif attr["format"] == 0x020B:
                attr["format_name"] = "snorm_10_10_10_2"
                normals_bytes = f"{buff_cursor.read_sint32():032b}"
                parts = [buff_cursor.to_signed(int(normals_bytes[x:x + 10], 2), 1024) / 1000 for x in
                         range(0, len(normals_bytes) - 2, 10)]
                vertices.append(
                    parts
                )
            elif attr["format"] == 0x0300:
                attr["format_name"] = "sint_8"
                vertices.append([
                    int(buff_cursor.read_sint8()),
                ])
            elif attr["format"] == 0x0304:
                attr["format_name"] = "sint_8_8"
                vertices.append([
                    int(buff_cursor.read_sint8()),
                    int(buff_cursor.read_sint8()),
                ])
            elif attr["format"] == 0x030A:
                attr["format_name"] = "sint_8_8_8_8"
                vertices.append([
                    int(buff_cursor.read_sint8()),
                    int(buff_cursor.read_sint8()),
                    int(buff_cursor.read_sint8()),
                    int(buff_cursor.read_sint8()),
                ])
            elif attr["format"] == 0x0806:
                attr["format_name"] = "float_32"
                vertices.append([
                    buff_cursor.read_float32(),
                ])
            elif attr["format"] == 0x0808:
                attr["format_name"] = "float_16_16"
                vertices.append([
                    buff_cursor.read_float16(),
                    buff_cursor.read_float16()
                ])
            elif attr["format"] == 0x080D:
                attr["format_name"] = "float_32_32"
                vertices.append([
                    buff_cursor.read_float32(),
                    buff_cursor.read_float32()
                ])
            elif attr["format"] == 0x080F:
                attr["format_name"] = "float_16_16_16_16"
                vertices.append([
                    buff_cursor.read_float16(),
                    buff_cursor.read_float16(),
                    buff_cursor.read_float16(),
                    buff_cursor.read_float16()
                ])
            elif attr["format"] == 0x0811:
                attr["format_name"] = "float_32_32_32"
                vertices.append([
                    buff_cursor.read_float32(),
                    buff_cursor.read_float32(),
                    buff_cursor.read_float32()
                ])
            elif attr["format"] == 0x0813:
                attr["format_name"] = "float_32_32_32_32"
                vertices.append([
                    buff_cursor.read_float32(),
                    buff_cursor.read_float32(),
                    buff_cursor.read_float32(),
                    buff_cursor.read_float32()
                ])
        return {
            "name": name,
            "data": {
                "attribute": attr,
                "buffer_header": buff_header,
                "vertices": vertices
            }
        }

    def parse_fvtx(self):
        fvtx_sections = {}
        for e in self.header["attributes_dict"]:
            fvtx = self.parse_attribute(e[1])
            fvtx_sections[fvtx["name"]] = fvtx["data"]
        return fvtx_sections
