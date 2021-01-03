#!/usr/bin/python3
# -*- coding: utf8 -*-

from fritzconnection import FritzConnection
import argparse

if __name__ == "__main__":
    services = {"Gäste-WLAN", "SmartHome"}
    ain = {"Gartenteich": "11657 0223468", "TV-Bank": "11630 0198785"}
    schalter = {"aus": "OFF", "an": "ON", "Wechsel": "TOGGLE"}

    parser = argparse.ArgumentParser(description="Schalte Aktoren der Fritz!Box.")
    parser.add_argument("service", help="Name des Service", choices=services)
    parser.add_argument("-a", "--aktor", help="nur Service SmartHome: Name des zu schaltenden Aktors",
                        choices=ain, default=None)
    parser.add_argument("-s", "--stellung", help="WLAN oder Aktor schalten",
                        choices=schalter, default="Wechsel")
    args = parser.parse_args()
    print(args.service)

    fritz_address = "192.168.10.1"
    fritz_user = "siri"
    fritz_password = "b=qa2YP`4EA4&2V_"

    fc = FritzConnection(address=fritz_address, user=fritz_user, password=fritz_password)
    if args.service == "Gäste-WLAN":
        old_enable = fc.call_action(service_name="WLANConfiguration3", action_name="GetInfo")["NewEnable"]
        if args.stellung == "an":
            new_enable = True
        elif args.stellung == "aus":
            new_enable = False
        else:
            new_enable = not old_enable
        print(old_enable, "->", new_enable)
        if old_enable != new_enable:
            fc.call_action(service_name="WLANConfiguration3", action_name="SetEnable", NewEnable=new_enable)
    elif args.service == "SmartHome":
        if args.aktor is not None:
            print(args.aktor, args.stellung)
            fc.call_action(service_name="X_AVM-DE_Homeauto1", action_name="SetSwitch",
                           NewAIN=ain[args.aktor], NewSwitchState=schalter[args.stellung])
        else:
            print("kein Aktor angegeben")
