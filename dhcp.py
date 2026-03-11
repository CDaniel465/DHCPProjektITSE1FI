from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["dhcp_simulation"]      # Datenbankname
collection = db["leases"]           # Collectionname

heute = datetime.now()

netzIp = "192.168.1."
IPListe = []
for item in collection.find():
    new_item = {
        "ip": item["ip"],
        "mac": item["mac"],
        "lease_end": item["lease_end"]  # bleibt datetime
    }
ende = False

#Checkt MAC nach Gültigkeit
def MAC_Überprüfer(clientinput):
    
    if clientinput == "":
        print("\033[31mBitte geben Sie etwas ein\033[0m")
        return False

    split_Ergebnis = str(clientinput).split(":")

    if len(split_Ergebnis) != 6:
        print("\033[31mIhre Eingabe ist nicht gültig, da diese\n"
              "aus weniger oder mehr als 6 Hexadezimalgruppen besteht.\033[0m")
        return False

    # Broadcastcheck
    if all(group.upper() == "FF" for group in split_Ergebnis):
        print("\033[31mBroadcasts sind nicht erlaubt.")
        return False
    elif all(group.upper() == "00" for group in split_Ergebnis):
        print("\033[31mNull-MAC-Adressen sind nicht erlaubt.\033[0m")
        return False

    # Hexadezimalcheck
    for group in split_Ergebnis:
        if len(group) != 2:
            print("\033[31mJede Gruppe muss genau 2 Zeichen haben.\033[0m")
            return False

        for char in group:
            if char.upper() not in "0123456789ABCDEF":
                print("\033[31mUngültige Hexadezimalzeichen gefunden.\033[0m")
                return False

    print("\033[32mMAC-Adresse ist gültig.\033[0m\n")
    return True
#Checkt MAC nach Gültigkeit

leasetime = heute + timedelta(days=7)
hostAdresse = 1
while ende == False:
    hostAdresse = 1
    #IPliste leeren wenn lease time vorbei
    heute = datetime.now()
    collection.delete_many({"lease_end": {"$lt": heute}})
    for i in IPListe:
        if heute > i[2]:
            IPListe.remove(i)

    def MacDuplikat(clientinput):
        for ip, mac, time in IPListe:
            if mac == clientinput:
                print(f"\033[31mClient hat bereits IP {ip}\033[0m")
                return True
        return False

    #Chat start
    print("1 Neuen Eintrag erstellen")
    print("2 Programm beenden")
    print("3 Gib das ganze Netzwerk aus")
    print("4 Eintrag löschen")
    auswahl = input("Geben Sie eine Auswahl ein: \n")

    #Neue IP registrieren
    if auswahl == "1":
        if len(IPListe) == 254:
            print("\033[31mKeine freien IP-Adressen mehr verfügbar.\033[0m")
        else:

            clientinput = input("Geben Sie Ihre Mac an: \n")

            if (MAC_Überprüfer(clientinput)== True):
                if MacDuplikat(clientinput):
                    continue
                while True:
                    ip_to_check = netzIp + str(hostAdresse)
                    is_available = True
                    for entry in IPListe:
                        if entry[1] == ip_to_check:
                            is_available = False
                            break
                    
                    if is_available:
                        lease_end = heute + timedelta(days=7)
                        clientenEintrag = [ip_to_check, clientinput, lease_end]
                        IPListe.append(clientenEintrag)
                        lease = {
                            "ip": ip_to_check,
                            "mac": clientinput,
                            "lease_end": lease_end
                        }
                        collection.insert_one(lease)
                        print(f"\033[32mIhre Neue IP ist: {ip_to_check}\033[0m")
                        break
                    hostAdresse += 1
                    if hostAdresse > 255:
                        print("\033[31mKeine freien IP-Adressen mehr verfügbar.\033[0m")
                        break
            else:
                print("\033[31mUngültige MAC-Adresse. Bitte versuchen Sie es erneut.\033[0m")
        

    #Programm beenden
    elif auswahl == "2":
        ende = True
        print("\033[31mProgrammende!\033[0m")

    #Ganze Netzwerkliste ausgeben
    elif auswahl == "3":
        for item in collection.find():
            print(f"\033[32mIP: {item['ip']} MAC: {item['mac']}" f" Lease Time: {item['lease_end']}\033[0m")
            print()
    elif auswahl == "4":
        ip_to_delete = input("Geben Sie die IP-Adresse ein, die Sie löschen möchten: \n")
        result = collection.delete_one({"ip": ip_to_delete})
        if result.deleted_count > 0:
            print(f"\033[32mEintrag mit IP {ip_to_delete} wurde gelöscht.\033[0m")
            for i in IPListe:
                if i["ip"] == ip_to_delete:
                    IPListe.remove(i)
                    break
        else:
            print(f"\033[31mKeine Einträge mit der IP {ip_to_delete} gefunden.\033[0m")
    else:   
        print()
        print("\033[31mBitte geben Sie eine gültige Eingabe ein!\033[0m")
    print()