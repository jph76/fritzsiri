#!/usr/bin/python3
# -*- coding: utf8 -*-

"""Switch Fritz!Box wireless guest access and SmartHome devices.

Copyright (C) 2021 Jan Heitkötter <jan@heitkoetter.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import itertools
from os import access, R_OK, path
from configparser import ConfigParser
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzwlan import FritzWLAN
from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation
from fritzconnection.core.exceptions import FritzServiceError
import argparse


def find_guest_wlan(fwlan, ssid):
    # Servicenummer des Gäste-WLAN anhand der SSID finden (normalerweise 3)
    # None, falls kein Gäste-WLAN vorhanden
    for n in itertools.count(1):
        fwlan.service = n
        try:
            if fwlan.ssid == ssid:
                return n
        except FritzServiceError:
            return None


def find_ains(fha):
    # SmartHome-Geräte finden
    # leeres Dict, falls keine vorhanden
    device_dict = {}
    for device in fha.device_informations():
        device_dict[device["NewDeviceName"]] = device["NewAIN"]
    return device_dict


if __name__ == "__main__":
    # Konfiguration auslesen
    if not access(path=path.expanduser("~/.fritzsiri.ini"), mode=R_OK):
        print("FATAL: config file not found")
        exit(1)
    config = ConfigParser()
    config.read(path.expanduser("~/.fritzsiri.ini"))
    fritz_address = config["fritzbox"]["address"]
    fritz_user = config["fritzbox"]["user"]
    fritz_password = config["fritzbox"]["password"]
    guest_ssid = config["wireless"]["guestssid"]

    # zulässige Argumente
    services = ["SmartHome", "WirelessGuestAccess"]
    schalter = {"off": "OFF", "on": "ON", "toggle": "TOGGLE"}
    # zulässige SmartHome-Geräte auslesen
    print("Reading SmartHome devices from Fritz!Box")
    fha = FritzHomeAutomation(address=fritz_address, user=fritz_user, password=fritz_password)
    geraete = find_ains(fha)

    # Argument Parser erzeugen
    parser = argparse.ArgumentParser(description="Simple Fritz!Box switching.")
    parser.add_argument("service", help="Service Name", choices=services)
    parser.add_argument("-d", "--device", help="Service SmartHome: device name",
                        choices=geraete, default=None)
    parser.add_argument("-s", "--switch", help="Switching operation",
                        choices=schalter, default="toggle")
    args = parser.parse_args()

    # API connection
    fc = FritzConnection(address=fritz_address, user=fritz_user, password=fritz_password)

    if args.service == "WirelessGuestAccess":
        # Servicenummer des Gäste-WLAN finden
        print("Searching for wireless guest access with SSID", guest_ssid)
        fwlan = FritzWLAN(address=fritz_address, user=fritz_user, password=fritz_password)
        service = find_guest_wlan(fwlan, guest_ssid)
        if service is None:
            print("FATAL: no wireless guest access found")
            exit(1)
        fwlan.service = service
        # aktuellen Zustand lesen
        old_enable = fc.call_action(service_name="WLANConfiguration" + str(fwlan.service),
                                    action_name="GetInfo")["NewEnable"]
        # neuen Zustand bestimmen
        if args.switch == "on":
            new_enable = True
        elif args.switch == "off":
            new_enable = False
        else:
            new_enable = not old_enable
        if old_enable != new_enable:
            tofo = {True: "on", False: "off"}
            print("Switching wireless guest access from", tofo[old_enable], "to", tofo[new_enable])
            fc.call_action(service_name="WLANConfiguration" + str(fwlan.service),
                           action_name="SetEnable", NewEnable=new_enable)
        else:
            print("No change in wireless guest access required")
    elif args.service == "SmartHome":
        # einfachere Schaltlogik, weil es hier TOGGLE gibt
        if geraete == {}:
            print("FATAL: no SmartHome devices available")
            exit(1)
        if args.device is not None:
            if fc.call_action(service_name="X_AVM-DE_Homeauto1",
                              action_name="GetSpecificDeviceInfos",
                              NewAIN=geraete[args.device])["NewSwitchIsEnabled"] == "DISABLED":
                print("FATAL: device does not allow switching")
                exit(1)
            print("New switch state for device", args.device, ":", args.switch)
            fc.call_action(service_name="X_AVM-DE_Homeauto1", action_name="SetSwitch",
                           NewAIN=geraete[args.device], NewSwitchState=schalter[args.switch])
        else:
            print("FATAL: device argument missing")
