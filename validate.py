#!/usr/bin/env python3

import os
import json

def log(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}")
    results["errors"].append(message)

# Load the configuration
log("Loading configuration from config.json")
with open('config.json', encoding='utf8') as config_json:
    config = json.load(config_json)

results = {"errors": [], "warnings": [], "datatype_tags": []}

# Ensure secondary and output directories exist
for directory in ["secondary", "output"]:
    if not os.path.exists(directory):
        os.mkdir(directory)
        log(f"Created directory: {directory}")
    else:
        log(f"Directory already exists: {directory}")

# Specifications for required and optional files for each datatype tag
specs = {
    "2phasemag": {"required": [ 
        "phase1", "phase1_json", 
        "phase2", "phase2_json", 
        "magnitude1", "magnitude1_json",
        "magnitude2", "magnitude2_json"
    ], "optional": []},
    "phasediff": {"required": [ 
        "phasediff", "phasediff_json",
        "magnitude1", "magnitude1_json"
    ], "optional": [
        "magnitude2", "magnitude2_json"
    ]},
    "single": {"required": [ 
        "fieldmap", "fieldmap_json",
        "magnitude", "magnitude_json"
    ], "optional": []},
    "pepolar": {"required": [ 
        "epi1", "epi1_json",
        "epi2", "epi2_json"
    ], "optional": []}
}

# Check for the fmap datatype in _inputs
log("Searching for fmap datatype in config['_inputs']")
fmap_input = None
for entry in config.get("_inputs", []):
    if entry.get("datatype") == "5c390505f9109beac42b00df":  # fmap datatype ID
        fmap_input = entry
        break

if not fmap_input:
    log_error("No fmap datatype found in config['_inputs']")
else:
    # Determine the type based on datatype_tags
    log("Determining the datatype tag based on 'datatype_tags'")
    datatype_tags = fmap_input.get("datatype_tags", [])
    valid_tag = None
    for tag in specs.keys():
        if tag in datatype_tags:
            valid_tag = tag
            results["datatype_tags"].append(tag)
            log(f"Detected valid datatype tag: {tag}")
            break
    
    if not valid_tag:
        log_error("No valid datatype tag found; expected one of: '2phasemag', 'phasediff', 'single', or 'pepolar'")
    else:
        # Validate required files for the identified datatype tag
        log(f"Validating required files for datatype tag: {valid_tag}")
        spec = specs[valid_tag]
        has_all_files = True
        for key in spec["required"]:
            if key not in config or not os.path.exists(config[key]):
                log_error(f"Missing required file: {key}")
                has_all_files = False
            else:
                log(f"Found required file: {config[key]}")
        
        # Copy required and optional files to the output directory
        if has_all_files:
            log("Copying required and optional files to 'output' directory")
            for key in spec["required"] + spec["optional"]:
                if key in config and os.path.exists(config[key]):
                    basename = os.path.basename(config[key])
                    output_path = os.path.join("output", basename)
                    if os.path.lexists(output_path):
                        os.remove(output_path)
                        log(f"Removed existing symlink: {output_path}")
                    os.symlink("../" + config[key], output_path)
                    log(f"Created symlink for {config[key]} at {output_path}")

# Write results to product.json
log("Writing results to product.json")
with open("product.json", "w") as fp:
    json.dump(results, fp)

log("Validation complete.")

