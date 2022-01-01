from bfres_parser import BfresParser
import json


bfres_file = BfresParser('binary.sbfres')

# File binary yaz0 decoded
# bfres_file.binary

# Friendly formatted data
# bfres_file.dict

# Raw data with a lot of things
# bfres_file.data

# Write data to json (can be quite large, more than 30 MB depending on the file opened)
with open('output.json', 'w') as output_file:
    output_file.write(json.dumps(bfres_file.dict, indent=4))

# Export every models to .obj format
obj_models = bfres_file.to_obj()
with open('models.obj', 'w') as wavefront_file:
    wavefront_file.write(obj_models)
