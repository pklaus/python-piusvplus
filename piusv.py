#!/usr/bin/env python

# Credits: user doing in the Raspberry Pi Forum (German)
# https://forum-raspberrypi.de/forum/thread/29737-pi-usv-monitoring-script/?postID=244579#post244579
# with 1st and 2nd changes as proposed by meigrafd in
# https://forum-raspberrypi.de/forum/thread/29737-pi-usv-monitoring-script/?postID=244611#post244611

import smbus
import sys
import time
import os


class PiUSV(object):
    def __init__(self):
        # Adresse
        self.address = 0x18
        # StatusByte
        self.data_0 = 1
        # Version
        self.data_1 = 12
        # Parameter
        self.data_2 = 10
        # Variablen
        self.par = [0,0,0,0,0,0,0,0,0,0]
        self.par_2 = [0,0,0,0,0]
        self.par_3 = [0,0,0,0,0]
        self.par_name = ["U_Batt (V)", "I_Rasp (A)", "U_Rasp (V)", "U_USB  (V)", "U_ext  (V)"]
        self.piusv = smbus.SMBus(1)

    # Firmware Version auslesen und in eine lesbare Zeile umwandeln
    def version(self):
        self.version = ""
        self.piusv.write_byte(self.address, 0x01)
        for i in range (self.data_1):
            try:
                self.version = self.version + chr(self.piusv.read_byte(self.address))
            except IOError, err:
                print "Fehler beim Lesen von Device 0x%02X" % self.address
        return self.version

    # Statusbyte auslesen
    def get_status(self):
        self.piusv.write_byte(self.address, 0x00)
        try:
            self.status = (self.piusv.read_byte(self.address))
        except IOError, err:
            print "Fehler beim Lesen von Device 0x%02X" % self.address
        return self.status

    # Die Parameter der PIUSV+ byteweise auslesen
    def get_parameter(self):
        self.piusv.write_byte(self.address, 0x02)
        for i in range (self.data_2):
            try:
                self.par[i] = self.piusv.read_byte(self.address)
            except IOError, err:
                print "Fehler beim Lesen von Device 0x%02X" % self.address
        return self.par

    # Umwandlung der Parameter in lesbare Werte(V,A)
    def word2float(self):
        for i in range (self.data_2/2):
            self.par_2[i] = (256*float(self.par[i*2])+(float(self.par[1+(i*2)])))/1000
        return self.par_2

    # Umwandlung der Parameter in lesbare Werte(mV,.A)
    def word2int(self):
        for i in range (self.data_2/2):
            self.par_2[i] = int(256*float(self.par[i*2])+(float(self.par[1+(i*2)])))
        return self.par_2

    # Werte mit Namen versehen
    def line(self):
        self.log = ""
        for i in range (self.data_2/2):
            self.log = self.log + " |"+"% 2.3f"% (self.par_2[i])+" "+self.par_name[i]
        self.log = ("%02s"% self.get_status())+self.log
        return self.log

    # Statusbyte auswerten, Mehrfachnennung moeglich
    def status2sent(self):
        stati = "StatusByte Bedeutung \n"
        status = self.get_status()
        if status&0x01==0x01:
            stati = stati + " 0000.0001 Spannungsversorgung von Micro-USB-Buchse" + "\n"
        if status&0x02==0x02:
            stati = stati + " 0000.0010 Spannungsversorgung von Uext" + "\n"
        if status&0x04==0x04:
            stati = stati + " 0000.0100 (Zu?) niedrige Batteriespannung" + "\n"
        if status&0x08==0x08:
            stati = stati + " 0000.1000 Akku wird geladen" + "\n"
        if status&0x10==0x10:
            stati = stati + " 0001.0000 Akku ist voll" + "\n"
        if status&0x20==0x20:
            stati = stati + " 0010.0000 Taster S1 betaetigt" + "\n"
        return (stati)

    def U_Batt(self):
        self.get_parameter()
        self.word2int()
        return self.par_2[0]

    def I_Rasp(self):
        self.get_parameter()
        self.word2int()
        return self.par_2[1]

    def U_Rasp(self):
        self.get_parameter()
        self.word2int()
        return self.par_2[2]

    def U_USB(self):
        self.get_parameter()
        self.word2int()
        return self.par_2[3]

    def U_ext(self):
        self.get_parameter()
        self.word2int()
        return self.par_2[4]
def main():
    optionen = "Moegliche Optionen:\n version \n status \n all \n log \n U_Batt \n I_Rasp \n U_Rasp \n U_USB \n U_ext"
    # Script mit diversen Optionen abarbeiten
    # Ohne Option wird eine Hilfe-Seite ausgegeben
    try:
        option = sys.argv[1]
    except:
        print optionen
        sys.exit(1)

    piusv = PiUSV()

    # Firmwareversion
    if option == "version":
        print piusv.version()

    # Status und Bedeutung
    elif option == "status":
        print piusv.status2sent()

    # Logdatei schreiben
    elif option == "log":
        piusv.get_parameter()
        piusv.word2float()
        log = time.strftime("%Y%m%d-%H%M%S")+" |"+ piusv.line() + "\n"
        with open('/var/log/PIUSV.log', 'a') as fh:
            fh.write(log)

    # Kommandozeilenausgabe komplett
    elif option == "all":
        piusv.get_parameter()
        piusv.word2float()
        all = piusv.line()
        print all + "\n" + piusv.status2sent()

    # Nur eine Zahl zur Weiterverarbeitung
    elif option == "U_Batt":
        print piusv.U_Batt()
    elif option == "I_Rasp":
        print piusv.I_Rasp()
    elif option == "U_Rasp":
        print piusv.U_Rasp()
    elif option == "U_USB":
        print piusv.U_USB()
    elif option == "U_ext":
        print piusv.U_ext()

    # Falsche Option, Hilfeseite ausgeben
    else:
        print optionen

if __name__ == '__main__':
    main()
