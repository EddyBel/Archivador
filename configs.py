import json

with open("config/extensions_config.json", "r") as f:
    extension_config = json.load(f)
    
with open("config/rename_config.json", "r") as f:
    rename_config = json.load(f)

    