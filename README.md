# fritzsiri

Unfortunately, the official Fritz! SmartHome app for iOS has neither widgets nor Siri support. This program is
designed to be called from iPhone using Apple Shortcuts (run ssh), allowing to be started from a widget or by yelling at Siri.

Copyright (C) 2021 Jan Heitkötter <jan@heitkoetter.net>

## Prerequisites

You’ll need a computer with a Linux oder BSD operating system with Python 3 installed and running a ssh server. Personally tested on Debian 10.

This program uses [fritzconnection](https://pypi.org/project/fritzconnection/) which requires Python 3.6.

The program requires a user to log into the Fritz!Box. You can use an already existing user or create a dedicated one. This user requires the following privileges:

* View and edit FRITZ!Box settings

* Control SmartHome devices

## Installation

Copy the Python file anywhere you like and make it executable. Edit and place the config file template as `.fritzsiri.ini` into the home folder of the user executing the Python file. You might want to `chmod 600 .fritzsiri.ini` to protect user credentials.

## Usage

`fritzsiri.py [-h] [-d] [-s] service`

`-h`: Display help including SmartHome device names

`-d`: SmartHome device name

`-s`: Switching operations, possible values: `off, on, toggle`

`service`: Service to execute, `SmartHome` or `WirelessGuestAccess`

## Examples

Toggle state of SmartHome device MySmartPowerSocket: `./fritzsiri.py SmartHome -d MySmartPowerSocket -s toggle`

Turn on wireless guest access: `./fritzsiri.py WirelessGuestAccess -s on`

You can call this program with parameters from Apple Shortcuts.

## License

This program is licensed under GPL-3.0