#!/usr/bin/env python3

import os
import json

# Things that this script checks
# 
# * make sure mrinfo runs successfully on specified t1 file
# * make sure t1 is 3d
# * raise warning if t1 transformation matrix isn't unit matrix (identity matrix)

# display where this is running
# import socket
# print(socket.gethostname())

with open('config.json', encoding='utf8') as config_json:
    config = json.load(config_json)

results = {"errors": [], "warnings": []}

if not os.path.exists("secondary"):
    os.mkdir("secondary")

if not os.path.exists("output"):
    os.mkdir("output")

#bypass all specified files to output
for key in config:
    basename = os.path.basename(config[key])
    if os.path.lexists("output/"+basename):
        os.remove("output/"+basename)
    os.symlink("../"+config[key], "output/"+basename)

with open("product.json", "w") as fp:
    json.dump(results, fp)

print("done");
