#!/usr/bin/env python
# -*- coding: utf-8 -*-

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

import json
import csv
import os.path

class DorisKmBot:
    def __init__(self, filepath, filename):
        self.filepath = filepath
        self.filename = filename

    def load_json(self):
        if os.path.isfile(self.filepath+"/"+self.filename):
            # read json file
            with open(self.filepath+"/"+self.filename, 'r') as myfile:
                data=myfile.read()
                # parse json file
                self.json_obj = json.loads(data)
        else:
            print(bcolors.ERROR + "ERROR: Keine Datei unter " + str(filepath) + " gefunden" + bcolors.ENDC)
            exit

    def write_to_csv(self, name="", km="", gefahren="", date=""):
        # open csv
        with open(self.filepath+"/fahrtenbuch.csv", mode='a') as fahrtenbuch_file:
            fahrtenbuch_writer = csv.writer(fahrtenbuch_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            fahrtenbuch_writer.writerow([name, km, gefahren, date])

    def run(self):
        self.load_json()
        # generate csv file with head row
        if not os.path.isfile(self.filepath+"/fahrtenbuch.csv"):
            self.write_to_csv("Name (Telegram)", "km-Stand", "km gefahren", "Datum")


        gesamt_km = {}
        last_km = 141442
        for message in self.json_obj["messages"]:
            try:
                user = message["from"].encode("utf-8")
                print "\nfrom ", user

                # add user to gesamt_km
                if not user in gesamt_km:
                    gesamt_km[user] = 0

                date = message["date"].replace("T", " ")[:16]
                print "on ", date

                text = message["text"]
                if isinstance(text, unicode) and text != "":
                    #text.encode("utf-8")
                    km = [int(s) for s in text.split() if s.isdigit()]
                    if len(km) == 0:
                        print(bcolors.ERROR + str(km) + " has no element" + bcolors.ENDC)
                        continue
                    elif km[0] < last_km or km[0] > last_km+10000:
                        print(bcolors.WARNING + str(km[0]) + " does not seem to be in a valid km range - omitting" + bcolors.ENDC)
                        continue
                    else:
                        km = km[0]
                    gefahren = km-last_km
                    last_km = km
                    print km, " km (gefahren: ", gefahren, ")"

                    gesamt_km[user] = gefahren + gesamt_km[user]

                    self.write_to_csv(user, km, gefahren, date)
                else: 
                    print(bcolors.WARNING + "\'" + str(text) + "\' is not a valid string (type: " + str(type(text)) + ") - omitting" + bcolors.ENDC)
            except:
                print(bcolors.ERROR + "could not process message " + str(message) + " - omitting" + bcolors.ENDC)
                
        # write summary
        self.write_to_csv() #empty line
        self.write_to_csv("Name", "alle km", "Beitrag ("+str(12)+" ct pro km)")
        for user, km in gesamt_km.iteritems():
            self.write_to_csv(user, km, str(km*0.12)+" €")

if __name__=='__main__':
    path = raw_input("Wo ist die Chat Export JSON Datei? (Bitte vollständigen Pfad angeben)\n")
    filepath = "/".join(path.split("/")[:-1])
    filename = path.split("/")[-1]
    Doris = DorisKmBot(filepath, filename)
    Doris.run()
