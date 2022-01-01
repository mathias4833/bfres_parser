# Bfres_parser (WiP)

This python module aims to parse Fres file format.

## What it can do for now

- Parse the header
- Parse FMDL sections
  - Retrieve the different attributes (position of the vertices, normals, UV maps, weight, ...)
  - Parse Material parameters, render info, shader options, render state
  - Parse bones

## Limitations

This is a work in progress so a lot of things will probably break. If you experience any bug, feel free to tell me. For now, only Wii U files are supported.  

## Usage

```python
from bfres_parser import BfresParser

bfres_file = BfresParser('file.sbfres')

# Raw data, contain almost everything that has been parsed
raw_data = bfres_file.data

# Friendly formatted data, way easier to read and to extract data from
friendly_data = bfres_file.dict

# Exports every models into a single .obj file
obj_models = bfres_file.to_obj()
with open('models.obj', 'w') as obj_file:
    obj_file.write(obj_models)
```
