from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["DHCP"]
collection = db["Geraete"]

base_IP = "192.168.1."


def neue_ip_erstellen():
    count = collection.count_documents({})
    return base_IP + str(count + 1)


def ip_zuweisen(mac):

    Geraet = collection.find_one({"mac": mac})

    if Geraet:
        print("MAC existiert bereits")
        return device["ip"]

    neue_ip = neue_ip_erstellen()

    data = {
        "mac": mac,
        "ip": new_ip,
        "timestamp": datetime.now()
    }

    collection.insert_one(data)

    return neue_ip


# Test
mac = input("MAC Adresse: ")

ip = ip_zuweisen(mac)

print("Zugewiesenw_ip", ip)
