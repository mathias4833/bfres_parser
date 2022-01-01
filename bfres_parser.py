from BfresParser.cursor import Cursor
from BfresParser.tools import open_bfres, read_string
from BfresParser.index_group import search_index_group
from BfresParser.Converter.wavefront_obj import ObjConverter
from BfresParser.FMDL.fmdl import Fmdl


class BfresParser:
    def __init__(self, filename):
        self.binary = open_bfres(filename)
        self.__header = self.__parse_header()
        self.__fmdl = self.__parse_fmdl()

        self.data = {
            "header": self.__header,
            "fmdl": self.__fmdl
        }

        self.dict = self.__create_friendly_dict()

    def __parse_header(self):
        cursor = Cursor(self.binary, 0)
        header = {}
        header["magic"] = cursor.read_chars(4)
        header["version"] = []
        for i in range(4):
            header["version"].append(cursor.read_uint8())
        header["bom"] = cursor.read_uint16()
        header["header_length"] = cursor.read_uint16()
        header["file_size"] = cursor.read_uint32()
        header["file_alignment"] = cursor.read_uint32()
        header["name"] = read_string(self.binary, cursor.read_offset())
        header["string_table_length"] = cursor.read_sint32()
        header["string_table_offset"] = cursor.read_offset()
        header["file_offsets"] = []
        header["file_counts"] = []
        for i in range(12):
            index_group_offset = cursor.read_offset()
            if index_group_offset != 0:
                header["file_offsets"].append(search_index_group(self.binary, index_group_offset))
            else:
                header["file_offsets"].append([])
        for i in range(12):
            header["file_counts"].append(cursor.read_uint16())
        header["user_pointer"] = cursor.read_uint32()

        return header

    def __parse_fmdl(self):
        fmdl_sections = []
        for entry in self.__header["file_offsets"][0]:
            fmdl_entry = Fmdl(self.binary, self.__header, entry[1])
            fmdl_sections.append(fmdl_entry.get_parsed_data())
        return fmdl_sections

    def __create_friendly_dict(self):
        infos = {
            "infos": {
                "name": self.__header["name"],
                "alignment": self.__header["file_alignment"],
                "version": self.__header["version"]
            },
            "models": []
        }
        for group in self.__fmdl:
            infos["models"].append({
                "infos": {
                    "name": group["header"]["name"],
                    "total_vertex_count": 0
                },
                "objects": [],
                "materials": [],
                "skeleton": {
                    "infos": {
                        "flags": group["fskl"]["header"]["flags"],
                    },
                    "bones": []
                }
            })
            for o in range(len(group["fvtx"])):
                infos["models"][-1]["objects"].append({
                    "infos": {
                        "name": group["header"]["fshp_dict"][group["fvtx"][o]["header"]["section_index"]][0],
                        "index": group["fvtx"][o]["header"]["section_index"],
                        "skin_count": group["fvtx"][o]["header"]["vertex_skin_count"],
                        "vertex_count": group["fvtx"][o]["header"]["vertex_count"]
                    },
                    "vertex_buffer": {},
                    "lod_models": []
                })
                infos["models"][-1]["infos"]["total_vertex_count"] += group["fvtx"][o]["header"]["vertex_count"]
                for attribute in group["fvtx"][o]["attributes"].keys():
                    infos["models"][-1]["objects"][-1]["vertex_buffer"][attribute] = {
                        "format": group["fvtx"][o]["attributes"][attribute]["attribute"]["format_name"],
                        "vertices": group["fvtx"][o]["attributes"][attribute]["vertices"]
                    }
            for m in range(len(group["fmat"])):
                infos["models"][-1]["materials"].append({
                    "infos": {
                        "name": group["header"]["fmat_dict"][m][0],
                        "shader_archive": group["fmat"][m]["shader_assign"]["archive_name"],
                        "shader_model": group["fmat"][m]["shader_assign"]["model_name"]
                    },
                    "texture_samplers": [],
                    "parameters": [],
                    "render_info": [],
                    "shader_options": [],
                    "render_state": group["fmat"][m]["render_state"]
                })
                for sampler in group["fmat"][m]["tex_sampler"]:
                    infos["models"][-1]["materials"][-1]["texture_samplers"].append({
                        "name": sampler["attribute_name"],
                        "GX2Sampler_struct1": sampler["GX2Sampler_struct1"],
                        "GX2Sampler_struct2": sampler["GX2Sampler_struct2"],
                        "GX2Sampler_struct3": sampler["GX2Sampler_struct3"],
                        "index": sampler["index"]
                    })
                for param in group["fmat"][m]["mat_param"]:
                    infos["models"][-1]["materials"][-1]["parameters"].append({
                        "name": param["variable_name"],
                        "value": param["value"]
                    })
                for info in group["fmat"][m]["render_info_param"]:
                    infos["models"][-1]["materials"][-1]["render_info"].append({
                        "name": info["name"],
                        "type": info["type"],
                        "data": info["data"]
                    })
                for option in group["fmat"][m]["shader_assign"]["param_dict"]:
                    infos["models"][-1]["materials"][-1]["shader_options"].append({
                        "name": option[0],
                        "value": option[1]
                    })
            for b in range(len(group["fskl"]["bones"])):
                infos["models"][-1]["skeleton"]["bones"].append({
                    "infos": {
                        "name": group["fskl"]["bones"][b]["name"],
                        "index": group["fskl"]["bones"][b]["index"],
                        "parent_index": group["fskl"]["bones"][b]["parent_index"],
                        "flags": group["fskl"]["bones"][b]["flags"],
                        "transform": {
                            "scale": group["fskl"]["bones"][b]["scale"],
                            "roation": group["fskl"]["bones"][b]["rotation"],
                            "translation": group["fskl"]["bones"][b]["translation"],
                        }
                    }
                })
            for s in range(len(group["fshp"])):
                for lod in group["fshp"][s]["lod_models"]:
                    infos["models"][-1]["objects"][group["fshp"][s]["header"]["fvtx_index"]]["lod_models"].append({
                        "infos": {
                            "primitive_type": lod["primitive_type_name"],
                            "index_format": lod["index_format_name"],
                        },
                        "primitives": []
                    })
                    for vis in lod["vis_groups"]:
                        infos["models"][-1]["objects"][group["fshp"][s]["header"]["fvtx_index"]]["lod_models"][-1][
                            "primitives"].append(
                            vis["primitives"]
                        )
        return infos

    def to_obj(self):
        return ObjConverter(self.dict).create_wavefront()
