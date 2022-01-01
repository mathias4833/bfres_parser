from BfresParser.cursor import Cursor
from BfresParser.index_group import search_index_group
from BfresParser.tools import read_string


class Fshp:
    def __init__(self, binary, offset):
        self.binary = binary
        self.offset = offset
        self.header = self.parse_header()

        self.parsed_data = {
            "header": self.header,
            "lod_models": self.parse_lod_models(),
            "vis_tree": self.parse_vis_group_tree()
        }

    def parse_header(self):
        cursor = Cursor(self.binary, self.offset)
        header = {}
        header["magic"] = cursor.read_chars(4)
        header["poly_name"] = read_string(self.binary, cursor.read_offset())
        header["flags"] = cursor.read_uint32()
        header["section_index"] = cursor.read_uint16()
        header["fmat_index"] = cursor.read_uint16()
        header["fskl_index"] = cursor.read_uint16()
        header["fvtx_index"] = cursor.read_uint16()
        header["fskl_bone_skin_index"] = cursor.read_uint16()
        header["vtx_skin_count"] = cursor.read_uint8()
        header["lod_mdl_count"] = cursor.read_uint8()
        header["key_shape_count"] = cursor.read_uint8()
        header["target_attr_count"] = cursor.read_uint8()
        header["vis_tree_node_count"] = cursor.read_uint16()
        header["radius"] = cursor.read_float32()
        header["fvtx_offset"] = cursor.read_offset()
        header["lod_mdl_offset"] = cursor.read_offset()
        header["fskl_index_offset"] = cursor.read_offset()
        header["key_shape_dict"] = search_index_group(self.binary, cursor.read_offset())
        header["vis_tree_nodes_offset"] = cursor.read_offset()
        header["vis_tree_ranges_offset"] = cursor.read_offset()
        header["vis_tree_indices_offset"] = cursor.read_offset()
        header["user_pointer"] = cursor.read_uint32()

        return header

    def parse_lod_models(self):
        primitive_type = {
            0x01: ["GX2_PRIMITIVE_POINTS", 1, 1],
            0x02: ["GX2_PRIMITIVE_LINES", 2, 2],
            0x03: ["GX2_PRIMITIVE_LINE_STRIP", 2, 1],
            0x04: ["GX2_PRIMITIVE_TRIANGLES", 3, 3],
            0x05: ["GX2_PRIMITIVE_TRIANGLE_FAN", 3, 1],
            0x06: ["GX2_PRIMITIVE_TRIANGLE_STRIP", 3, 1],
            0x0a: ["GX2_PRIMITIVE_LINES_ADJACENCY", 4, 4],
            0x0b: ["GX2_PRIMITIVE_LINE_STRIP_ADJACENCY", 4, 1],
            0x0c: ["GX2_PRIMITIVE_TRIANGLES_ADJACENCY", 6, 6],
            0x0d: ["GX2_PRIMITIVE_TRIANGLE_STRIP_ADJACENCY", 6, 2],
            0x11: ["GX2_PRIMITIVE_RECTS", 3, 3],
            0x12: ["GX2_PRIMITIVE_LINE_LOOP", 2, 1],
            0x13: ["GX2_PRIMITIVE_QUADS", 4, 4],
            0x14: ["GX2_PRIMITIVE_QUAD_STRIP", 4, 2],
            0x82: ["GX2_PRIMITIVE_TESSELLATE_LINES", 2, 2],
            0x83: ["GX2_PRIMITIVE_TESSELLATE_LINE_STRIP", 2, 1],
            0x84: ["GX2_PRIMITIVE_TESSELLATE_TRIANGLES", 3, 3],
            0x86: ["GX2_PRIMITIVE_TESSELLATE_TRIANGLE_STRIP", 2, 1],
            0x93: ["GX2_PRIMITIVE_TESSELLATE_QUADS", 4, 4],
            0x94: ["GX2_PRIMITIVE_TESSELLATE_QUAD_STRIP", 4, 2]
        }
        index_format = {
            0: ["GX2_INDEX_FORMAT_U16_LE", "<H"],
            1: ["GX2_INDEX_FORMAT_U32_LE", "<I"],
            4: ["GX2_INDEX_FORMAT_U16", ">H"],
            9: ["GX2_INDEX_FORMAT_U32", ">I"]
        }

        lod_models = []
        for m in range(self.header["lod_mdl_count"]):
            cursor = Cursor(self.binary, self.header["lod_mdl_offset"] + m * 0x1C)
            lod = {}
            lod["primitive_type"] = cursor.read_uint32()
            lod["primitive_type_name"] = primitive_type[lod["primitive_type"]][0]
            lod["index_format"] = cursor.read_uint32()
            lod["index_format_name"] = index_format[lod["index_format"]][0]
            lod["point_count"] = cursor.read_uint32()
            lod["vis_group_count"] = cursor.read_uint16()
            cursor.skip_bytes(2)
            lod["vis_group_offset"] = cursor.read_offset()
            lod["index_buffer_offset"] = cursor.read_offset()
            lod["skip_vertices"] = cursor.read_uint32()

            vis_groups = []
            for g in range(lod["vis_group_count"]):
                cursor.go_to(lod["vis_group_offset"] + g * 0x08)
                vis_groups.append({
                    "offset": cursor.read_uint32(),
                    "count": cursor.read_uint32()
                })

            cursor.go_to(lod["index_buffer_offset"])
            lod["index_buffer"] = {
                "data_pointer": cursor.read_uint32(),
                "size": cursor.read_uint32(),
                "handle": cursor.read_uint32(),
                "stride": cursor.read_uint16(),
                "buffering_count": cursor.read_uint16(),
                "context_pointer": cursor.read_uint32(),
                "data_offset": cursor.read_offset()
            }
            lod["vis_groups"] = []
            for vis in vis_groups:
                cursor.go_to(lod["index_buffer"]["data_offset"] + vis["offset"])
                vertices = []
                for v in range(vis["count"]):
                    vertices.append(cursor.read_custom(index_format[lod["index_format"]][1])[0])
                vis["primitives"] = [vertices[x:x + primitive_type[lod["primitive_type"]][1]] for x in
                                     range(0, len(vertices), primitive_type[lod["primitive_type"]][1])]
                lod["vis_groups"].append(vis)
            lod_models.append(lod)

        return lod_models

    def parse_vis_group_tree(self):
        vis_tree_nodes = []
        vis_tree_ranges = []
        for n in range(self.header["vis_tree_node_count"]):
            cursor = Cursor(self.binary, self.header["vis_tree_nodes_offset"])
            vis_node = {}
            vis_node["left_child_index"] = cursor.read_uint16()
            vis_node["right_child_index"] = cursor.read_uint16()
            cursor.skip_bytes(2)
            vis_node["next_sibling_index"] = cursor.read_uint16()
            vis_node["vis_group_index"] = cursor.read_uint16()
            vis_node["vis_group_count"] = cursor.read_uint16()
            vis_tree_nodes.append(vis_node)
            
            cursor.go_to(self.header["vis_tree_ranges_offset"])
            vis_range = {}
            vis_range["center"] = [
                cursor.read_float32(),  # X
                cursor.read_float32(),  # Y
                cursor.read_float32()   # Z
            ]
            vis_range["extent"] = [
                cursor.read_float32(),  # X
                cursor.read_float32(),  # Y
                cursor.read_float32()   # Z
            ]
            vis_tree_ranges.append(vis_range)

        return {
            "nodes": vis_tree_nodes,
            "ranges": vis_tree_ranges
        }
