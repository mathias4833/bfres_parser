import struct


class Cursor:
    def __init__(self, binary, offset, big_endian=True):
        self.binary = binary
        self.offset = offset
        self.endian = ">" if big_endian else "<"

        self.format = {
            "char": "s",        # Char                  --> size 1
            "uint128": "Q",     # Unsigned Long Long    --> size 8
            "uint64": "L",      # Unsigned Long         --> size 4
            "uint32": "I",      # Unsigned Int          --> size 4
            "uint16": "H",      # Unsigned Short        --> size 2
            "uint8": "B",       # Unsigned Int          --> size 1
            "sint128": "q",     # Signed Long Long      --> size 8
            "sint64": "l",      # Signed Long           --> size 4
            "sint32": "i",      # Signed Int            --> size 4
            "sint16": "h",      # Signed Short          --> size 2
            "sint8": "b",       # Signed Int            --> size 1
            "float16": "e",     # Float                 --> size 2
            "float32": "f",     # Float                 --> size 4
            "double": "d"       # Double                --> size 8
        }

    def __read_bytes(self, binary_format, tuple_format=False):
        size = struct.calcsize(binary_format)
        data = struct.unpack(binary_format, self.binary[self.offset:self.offset + size])
        self.skip_bytes(size)
        if tuple_format:
            return data
        return data[0]

    def skip_bytes(self, size=1):
        self.offset += size

    def go_to(self, offset):
        self.offset = offset

    def read_offset(self, custom_offset=0, binary_format="sint32"):
        bformat = self.endian + self.format[binary_format]
        offset = self.__read_bytes(bformat)
        if offset == 0:
            return 0
        return offset + self.offset - struct.calcsize(bformat) + custom_offset

    def read_custom(self, custom):
        return self.__read_bytes(custom, tuple_format=True)

    def to_signed(self, number, number_range):
        return number - number_range * (number >= int(number_range/2))

    def read_chars(self, count=1):
        return self.__read_bytes(f"{self.endian}{count}{self.format['char']}").decode('ascii')

    def read_uint128(self):
        return self.__read_bytes(self.endian + self.format["uint128"])

    def read_uint64(self):
        return self.__read_bytes(self.endian + self.format["uint64"])

    def read_uint32(self):
        return self.__read_bytes(self.endian + self.format["uint32"])

    def read_uint16(self):
        return self.__read_bytes(self.endian + self.format["uint16"])

    def read_uint8(self):
        return self.__read_bytes(self.endian + self.format["uint8"])

    def read_sint128(self):
        return self.__read_bytes(self.endian + self.format["sint128"])

    def read_sint64(self):
        return self.__read_bytes(self.endian + self.format["sint64"])

    def read_sint32(self):
        return self.__read_bytes(self.endian + self.format["sint32"])

    def read_sint16(self):
        return self.__read_bytes(self.endian + self.format["sint16"])

    def read_sint8(self):
        return self.__read_bytes(self.endian + self.format["sint8"])

    def read_float16(self):
        return self.__read_bytes(self.endian + self.format["float16"])

    def read_float32(self):
        return self.__read_bytes(self.endian + self.format["float32"])

    def read_double(self):
        return self.__read_bytes(self.endian + self.format["double"])

