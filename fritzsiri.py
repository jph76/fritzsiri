#!/usr/bin/python3
# -*- coding: utf8 -*-

from fritzconnection import FritzConnection
import argparse

if __name__ == "__main__":
    ain = {"Gartenteich": "11657 0223468", "TV-Bank": "11630 0198785"}
    schalter = {"aus": "OFF", "an": "ON", "Wechsel": "TOGGLE"}

    parser = argparse.ArgumentParser(description="Schalte Aktoren der Fritz!Box.")
    parser.add_argument("-a", "--aktor", help="Name des zu schaltenden Aktors",
                        choices=ain, required=True)
    parser.add_argument("-s", "--stellung", help="Neue Schalterstellung des Aktors",
                        choices=schalter, default="Wechsel")

    args=parser.parse_args()

    fritz_address = "192.168.10.1"
    fritz_user = "siri"
    fritz_password = "b=qa2YP`4EA4&2V_"

    fc = FritzConnection(address=fritz_address, user=fritz_user, password=fritz_password)
    ca = fc.call_action(service_name="X_AVM-DE_Homeauto1", action_name="SetSwitch",
                        NewAIN=ain[args.aktor], NewSwitchState=schalter[args.stellung])
