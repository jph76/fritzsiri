#!/usr/bin/python3
# -*- coding: utf8 -*-

import itertools
from configparser import ConfigParser
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzwlan import FritzWLAN
from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation
from fritzconnection.core.exceptions import FritzServiceError
import argparse

def find_guest_wlan(fwlan, ssid):
    # finds service number of guest WLAN
    # returns None if no guest WLAN found
    for n in itertools.count(1):
        fwlan.service = n
        try:
            if fwlan.ssid == ssid:
                return n
        except FritzServiceError:
            return None

def find_ains(fha):
    # finds SmartHome actors
    # returns empty dict if no actors availble
    device_dict = {}
    for device in fha.device_informations():
        device_dict[device["NewDeviceName"]] = device["NewAIN"]
    return device_dict

if __name__ == "__main__":
    # read config
    config = ConfigParser()
    config.read("fritzsiri.ini")
    fritz_address = config["fritzbox"]["address"]
    fritz_user = config["fritzbox"]["user"]
    fritz_password = config["fritzbox"]["password"]

    # valid values for arguments
    services = {"Gäste-WLAN", "SmartHome"}
    schalter = {"aus": "OFF", "an": "ON", "Wechsel": "TOGGLE"}
    fha = FritzHomeAutomation(address=fritz_address, user=fritz_user, password=fritz_password)
    ain = find_ains(fha)

    # create argument parser
    parser = argparse.ArgumentParser(description="Schalte Aktoren der Fritz!Box.")
    parser.add_argument("service", help="Name des Service", choices=services)
    parser.add_argument("-a", "--aktor", help="nur Service SmartHome: Name des zu schaltenden Aktors",
                        choices=ain, default=None)
    parser.add_argument("-s", "--stellung", help="WLAN oder Aktor schalten",
                        choices=schalter, default="Wechsel")
    args = parser.parse_args()
    print(args.service)

    # API connection
    fc = FritzConnection(address=fritz_address, user=fritz_user, password=fritz_password)

    if args.service == "Gäste-WLAN":
        # find out service number of guest WLAN (usually 3)
        fwlan = FritzWLAN(address=fritz_address, user=fritz_user, password=fritz_password)
        service = find_guest_wlan(fwlan, config["wlan"]["guestssid"])
        if service is None:
            print("No guest WLAN found")
            exit(1)
        fwlan.service = service
        # read current state of guest WLAN
        old_enable = fc.call_action(service_name="WLANConfiguration" + str(fwlan.service),
                                    action_name="GetInfo")["NewEnable"]
        # switching logic
        if args.stellung == "an":
            new_enable = True
        elif args.stellung == "aus":
            new_enable = False
        else:
            new_enable = not old_enable
        print(old_enable, "->", new_enable)
        if old_enable != new_enable:
            fc.call_action(service_name="WLANConfiguration" + str(fwlan.service),
                           action_name="SetEnable", NewEnable=new_enable)
    elif args.service == "SmartHome":
        # simpler logic with built-in toggle
        if ain == {}:
            print("No smarthome actors available")
            exit(1)
        if args.aktor is not None:
            print(args.aktor, args.stellung)
            fc.call_action(service_name="X_AVM-DE_Homeauto1", action_name="SetSwitch",
                           NewAIN=ain[args.aktor], NewSwitchState=schalter[args.stellung])
        else:
            print("missing actor")

