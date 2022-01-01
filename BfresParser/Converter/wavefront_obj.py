class ObjConverter:
    def __init__(self, data):
        self.data = data

    def create_wavefront(self):
        file = ""

        total_vertices = 0
        for models in self.data["models"]:
            for obj in models["objects"]:
                file += f"\no {obj['infos']['name']}\ns 1"
                attributes = [
                    {"name": "_p0", "obj_prefix": "v", "allow_negative": True},
                    {"name": "_u0", "obj_prefix": "vt", "allow_negative": False},
                ]
                # Attributes
                for attr in attributes:
                    if attr["name"] in obj["vertex_buffer"].keys():
                        for vertex in obj["vertex_buffer"][attr["name"]]["vertices"]:
                            file += f"\n{attr['obj_prefix']}"
                            for value in vertex:
                                if not attr["allow_negative"]:
                                    value = value * 0.5 + 0.5
                                file += f" {value}"

                # Primitives
                for primitives_group in obj["lod_models"][0]["primitives"]:
                    for primitive in primitives_group:
                        file += "\nf"
                        for index in primitive:
                            file += " "
                            if attributes[0]["name"] in obj["vertex_buffer"].keys():
                                file += f"{index + total_vertices + 1}"
                                file += "/"
                                if "_u0" in obj["vertex_buffer"].keys():
                                    file += f"{index + total_vertices + 1}"
                total_vertices += obj["infos"]["vertex_count"]
        return file
