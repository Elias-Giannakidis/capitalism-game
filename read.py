import json
import random

def readConfiguration():
    with open("configuration.json", 'r') as f:
        data = json.load(f)
    return data

def getProducts():
    data = readConfiguration()
    materials = []
    for mat in data["materials"]:
        materials.append(mat["path"])
    return materials

def getPlayers(num):
    conf = readConfiguration()
    players = conf["capitalism"]["players"]
    return random.sample(players, num)




