import json

class Config():
    pass

with open("./config.json") as file:
    CONFIG = json.load(file)

for k, v in CONFIG.items():
    setattr(Config, k, v)
