#!/usr/bin/env python

# Credits: user doing in the Raspberry Pi Forum (German)
# https://forum-raspberrypi.de/forum/thread/29737-pi-usv-monitoring-script/?postID=244579#post244579
# with 1st changes as proposed by meigrafd in
# https://forum-raspberrypi.de/forum/thread/29737-pi-usv-monitoring-script/?postID=244611#post244611

import smbus
import sys
import time
import os
 
# Pi USV+ Adresse
address = 0x18
 
# StatusByte
data_0 = 1

# Version
data_1 = 12

# Parameter (I/U)
data_2 = 10
 
# Globale Variablen
par = [0,0,0,0,0,0,0,0,0,0]
par_2 = [0,0,0,0,0]
par_3 = [0,0,0,0,0]
par_name = ["U_Batt (V)", "I_Rasp (A)", "U_Rasp (V)", "U_USB  (V)", "U_ext  (V)"]
log = ""
version = ""
status = ""
stati = ""
optionen = "Moegliche Optionen:\n version \n status \n all \n log \n U_Batt \n I_Rasp \n U_Rasp \n U_USB \n U_ext"
 
# Handle
piusv = smbus.SMBus(1)

# Statusbyte auslesen
def get_status(piusv, address):
    piusv.write_byte(address, 0x00)
    try:
        status = (piusv.read_byte(address))
    except IOError, err:
        print "Fehler beim Lesen von Device 0x%02X" % address
        sys.exit(-1)
    return status

# Firmware Version auslesen und in eine lesbare Zeile umwandeln
def version(piusv, address, data_1):
    version = ""
    piusv.write_byte(address, 0x01)
    for i in range (data_1):
        try:
            version = version + chr(piusv.read_byte(address))
        except IOError, err:
            print "Fehler beim Lesen von Device 0x%02X" % address
            sys.exit(-1)
    return version

# Die Parameter der PIUSV+ byteweise auslesen
def get_parameter():
    piusv.write_byte(address, 0x02)
    for i in range (data_2):
        try:
            par[i] = piusv.read_byte(address)
        except IOError, err:
            print "Fehler beim Lesen von Device 0x%02X" % address
            exit(-1)
    return par

# Umwandlung der Parameter in lesbare Werte(V,A)
def word2float(par, data_2):
    for i in range (data_2/2):
          par_2[i] = (256*float(par[i*2])+(float(par[1+(i*2)])))/1000
    return par_2

# Umwandlung der Parameter in lesbare Werte(mV,.A)
def word2int(par, data_2):
    for i in range (data_2/2):
        par_2[i] = int(256*float(par[i*2])+(float(par[1+(i*2)])))
    return par_2

# Werte mit Namen versehen
def line(par_2, data_2):
    log = ""
    for i in range (data_2/2):
        log = log+" |"+"% 2.3f"% (par_2[i])+" "+par_name[i]
    log = ("%02s"% get_status(piusv, address))+log
    return log

# Statusbyte auswerten, Mehrfachnennung moeglich
def status2sent():
    stati = "StatusByte Bedeutung \n"
    status = get_status(piusv, address)
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

def U_Batt():
    get_parameter()
    word2int(par, data_2)
    return par_2[0]

def I_Rasp():
    get_parameter()
    word2int(par, data_2)
    return par_2[1]

def U_Rasp():
    get_parameter()
    word2int(par, data_2)
    return par_2[2]

def U_USB():
    get_parameter()
    word2int(par, data_2)
    return par_2[3]

def U_ext():
    get_parameter()
    word2int(par, data_2)
    return par_2[4]


def main():
    # Script mit diversen Optionen abarbeiten
    # Ohne Option wird eine Hilfe-Seite ausgegeben
    try:
        option = sys.argv[1]
    except:
        print optionen
        sys.exit(1)

    # Firmwareversion
    if option == "version":
        print version(piusv, address, data_1)
 
    # Status und Bedeutung
    elif option == "status":
        print status2sent()

    # Logdatei schreiben
    elif option == "log":
        get_parameter()
        word2float(par, data_2)
        log = time.strftime("%Y%m%d-%H%M%S")+" |"+line(par_2, data_2) + "\n"
        with open('/var/log/PIUSV.log', 'a') as fh:
            fh.write(log)

    # Kommandozeilenausgabe komplett
    elif option == "all":
        get_parameter()
        word2float(par, data_2)
        all = line(par_2, data_2)
        print all + "\n" + status2sent()
 
    # Nur eine Zahl zur Weiterverarbeitung
    elif option == "U_Batt":
        print U_Batt()
    elif option == "I_Rasp":
        print I_Rasp()
    elif option == "U_Rasp":
        print U_Rasp()
    elif option == "U_USB":
        print U_USB()
    elif option == "U_ext":
        print U_ext()
 
    # Falsche Option, Hilfeseite ausgeben
    else:
        print optionen


if __name__ == '__main__':
    main()
