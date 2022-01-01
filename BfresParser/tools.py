import os
import oead


def open_bfres(path):
    with open(path, "rb") as f:
        data = f.read()
    extension = os.path.splitext(path)[1]
    if extension.startswith(".s"):
        return oead.yaz0.decompress(data)
    else:
        return data


def read_string(binary, offset):
    next_offset = offset
    name = ""
    while True:
        character = binary[next_offset]
        if character != 0:
            name += chr(character)
        else:
            return name
        next_offset += 1
