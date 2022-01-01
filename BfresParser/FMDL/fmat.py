from BfresParser.cursor import Cursor
from BfresParser.tools import read_string
from BfresParser.index_group import search_index_group


class Fmat:
    def __init__(self, binary, version, offset):
        self.binary = binary
        self.version = version
        self.offset = offset
        self.header = self.parse_header()

        self.parsed_data = {
            "header": self.header,
            "render_info_param": self.parse_render_info_params(),
            "tex_sampler": self.parse_texture_samplers(),
            "mat_param": self.parse_mat_params(),
            "render_state": self.parse_render_state(),
            "shader_assign": self.parse_shader_assign()
        }

    def parse_header(self):
        cursor = Cursor(self.binary, self.offset)
        header = {}
        header["magic"] = cursor.read_chars(4)
        header["mat_name"] = read_string(self.binary, cursor.read_offset())
        header["mat_flags"] = cursor.read_uint32()
        header["section_index"] = cursor.read_uint16()
        header["render_info_count"] = cursor.read_uint16()
        header["tex_ref_count"] = cursor.read_uint8()
        header["tex_sampler_count"] = cursor.read_uint8()
        header["mat_param_count"] = cursor.read_uint16()
        header["volatile_param_count"] = cursor.read_uint16()
        header["mat_param_length"] = cursor.read_uint16()
        header["raw_param_length"] = cursor.read_uint16()
        header["user_data_entry_count"] = cursor.read_uint16()
        header["render_info_param_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["render_state_offset"] = cursor.read_offset()
        header["shader_assign_offset"] = cursor.read_offset()
        header["tex_ref_offset"] = cursor.read_offset()
        header["tex_sampler_offset"] = cursor.read_offset()
        header["tex_sampler_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["mat_param_offset"] = cursor.read_offset()
        header["mat_param_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["mat_param_data_offset"] = cursor.read_offset()
        header["user_data_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["volatile_flags_offset"] = cursor.read_offset()
        header["user_pointer"] = cursor.read_sint32()

        return header

    def parse_render_info_params(self):
        params = []
        for e in self.header["render_info_param_dict"]:
            cursor = Cursor(self.binary, e[1])
            render_info = {}
            render_info["array_length"] = cursor.read_uint16()
            render_info["type"] = cursor.read_uint8()
            cursor.skip_bytes()
            render_info["name"] = read_string(self.binary, cursor.read_offset())
            render_info["data"] = []
            for i in range(render_info["array_length"]):
                if render_info["type"] == 0:
                    render_info["data"].append([
                        cursor.read_sint32(),
                        cursor.read_sint32()
                    ])
                if render_info["type"] == 1:
                    render_info["data"].append([
                        cursor.read_float32(),
                        cursor.read_float32()
                    ])
                if render_info["type"] == 2:
                    render_info["data"].append(
                        read_string(self.binary, cursor.read_offset())
                    )
            params.append(render_info)

        return params

    def parse_texture_samplers(self):
        samplers = []
        for e in self.header["tex_sampler_dict"]:
            cursor = Cursor(self.binary, e[1])
            samplers.append({
                "GX2Sampler_struct1": cursor.read_uint32(),
                "GX2Sampler_struct2": cursor.read_uint32(),
                "GX2Sampler_struct3": cursor.read_uint32(),
                "handle": cursor.read_uint32(),
                "attribute_name": read_string(self.binary, cursor.read_offset()),
                "index": cursor.read_uint8()
            })

        return samplers

    def parse_mat_params(self):
        variable_format = {
            0: '>I',        # 1 boolean value.
            1: '>2I',       # 2-component boolean vector.
            2: '>3I',       # 3-component boolean vector.
            3: '>4I',       # 4-component boolean vector.
            4: '>i',        # 1 signed integer value.
            5: '>2i',       # 2-component signed integer vector.
            6: '>3i',       # 3-component signed integer vector.
            7: '>4i',       # 4-component signed integer vector.
            8: '>I',        # 1 unsigned integer value.
            9: '>2I',       # 2-component unsigned integer vector.
            10: '>3I',      # 3-component unsigned integer vector.
            11: '>4I',      # 4-component unsigned integer vector.
            12: '>f',       # 1 floating point value.
            13: '>2f',      # 2-component floating point vector.
            14: '>3f',      # 3-component floating point vector.
            15: '>4f',      # 4-component floating point vector.
            17: '>4f',      # 2×2 floating point matrix.
            18: '>6f',      # 2×3 floating point matrix.
            19: '>8f',      # 2×4 floating point matrix.
            21: '>6f',      # 3×2 floating point matrix.
            22: '>9f',      # 3×3 floating point matrix.
            23: '>12f',     # 3×4 floating point matrix.
            25: '>8f',      # 4×2 floating point matrix.
            26: '>12f',     # 4×3 floating point matrix.
            27: '>16f',     # 4×4 floating point matrix.
            28: '>5f',      # 2D SRT data.
            29: '>9f',      # 3D SRT data.
            30: '>I 5f',    # Texture SRT data.
            31: '>12I'      # Texture SRT data multiplied by a 3x4 matrix referenced by the matrix pointer.
        }

        params = []
        version = 0
        for i in range(len(self.version)):
            version += 10 ** (len(self.version) - 1 - i) * self.version[i]

        for e in self.header["mat_param_dict"]:
            cursor = Cursor(self.binary, e[1])
            mat_param = {}
            mat_param["type"] = cursor.read_uint8()
            mat_param["size"] = cursor.read_uint8()
            mat_param["offset"] = cursor.read_uint16() + self.header["mat_param_data_offset"]
            if version >= 3400:
                cursor.skip_bytes(12)
            elif 3300 <= version < 3400:
                cursor.skip_bytes(16)
            mat_param["variable_name"] = read_string(self.binary, cursor.read_offset())
            cursor.go_to(mat_param["offset"])
            mat_param["value"] = cursor.read_custom(variable_format[mat_param["type"]])
            params.append(mat_param)

        return params

    def parse_render_state(self):
        cursor = Cursor(self.binary, self.header["render_state_offset"])
        render_state = {}
        render_state["flags"] = cursor.read_uint32()
        render_state["poly_ctrl"] = cursor.read_uint32()
        render_state["depth_ctrl"] = cursor.read_uint32()
        render_state["alpha_test"] = [
            cursor.read_uint32(),
            cursor.read_float32()
        ]
        render_state["color_ctrl"] = cursor.read_uint32()
        render_state["blend_ctrl"] = [
            cursor.read_uint32(),
            cursor.read_uint32()
        ]
        render_state["blend_color"] = [
            cursor.read_float32(),  # R
            cursor.read_float32(),  # G
            cursor.read_float32(),  # B
            cursor.read_float32(),  # A
        ]

        return render_state

    def parse_shader_assign(self):
        cursor = Cursor(self.binary, self.header["shader_assign_offset"])
        shader_assign = {}
        shader_assign["archive_name"] = read_string(self.binary, cursor.read_offset())
        shader_assign["model_name"] = read_string(self.binary, cursor.read_offset())
        shader_assign["revision"] = cursor.read_uint32()
        shader_assign["vtx_shader_input_count"] = cursor.read_uint8()
        shader_assign["fragment_shader_input_count"] = cursor.read_uint8()
        shader_assign["param_count"] = cursor.read_uint16()
        shader_assign["vtx_shader_input_dict"] = search_index_group(self.binary, cursor.read_offset())
        shader_assign["fragment_shader_input_dict"] = search_index_group(self.binary, cursor.read_offset())
        shader_assign["param_dict"] = [[shader_option[0], read_string(self.binary, shader_option[1])] for shader_option in search_index_group(self.binary, cursor.read_offset())]

        return shader_assign
