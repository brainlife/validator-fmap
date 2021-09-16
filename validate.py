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

results = {"errors": [], "warnings": [], "datatype_tags": []}

if not os.path.exists("secondary"):
    os.mkdir("secondary")

if not os.path.exists("output"):
    os.mkdir("output")

specs = {
        "2phasemag": {"required": [ 
            "phase1", "phase1_json", 
            "phase2", "phase2_json", 
            "magnitude1", "magnitude1_json",
            "magnitude2", "magnitude2_json",
        ], "optional": []},

        "phasediff": {"required": [ 
            "phasediff", "phasediff_json",
            "magnitude1", "magnitude1_json",
        ], "optional": [
            "magnitude2", "magnitude2_json"
        ]},

        "single": {"required": [ 
            "magnitude", "magnitude_json",
            "fieldmap", "fieldmap_json"
        ], "optional": []},

        "pepolar": {"required": [ 
            "epi1", "epi1_json",
            "epi2", "epi2_json"
        ], "optional": []}
}

type = None
for subtype in specs:
    spec = specs[subtype]
    print("trying as", subtype)

    #see if all required files are present
    haskeys = True
    for key in spec["required"]:
        #print("checking", key)
        if key not in config:
            haskeys = False
    if not haskeys:
        print(" .. nope")
        continue

    print("looks like", subtype)
    type = subtype

    hasfiles = True
    for key in spec["required"]:
        if not os.path.exists(config[key]):
            results["errors"].append("missing requried file %s" % config[key])
            hasfiles = False
    if not hasfiles:
        print("required files missing")
        break

    #copy required files
    for key in spec["required"]:
        print("copying", key, config[key])
        basename = os.path.basename(config[key])
        if os.path.lexists("output/"+basename):
            os.remove("output/"+basename)
        os.symlink("../"+config[key], "output/"+basename)

    for key in spec["optional"]:
        if key in config:
            if os.path.exists(config[key]):
                print("copying", key, config[key])
                basename = os.path.basename(config[key])
                if os.path.lexists("output/"+basename):
                    os.remove("output/"+basename)
                os.symlink("../"+config[key], "output/"+basename)
    break

if type == None:
    results["errors"].append("couldn't figure out the fmap subtype")
else:
    results["datatype_tags"].append(type)

if len(results["errors"]):
    print(results)
            
#bypass all specified files to output
with open("product.json", "w") as fp:
    json.dump(results, fp)

print("done");
