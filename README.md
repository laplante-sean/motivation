# Motivation

So you wanna play video games and get fit, but you want to play real video games because fitness video games get old too fast? Well if you have a supported smart trainer, now you can!

"Motivation" is Stationary Bike "Smart" trainer gaming motivator. It connects to Bluetooth Low-Energy (LE) smart trainers and disables your game controller if you drop below a configured power output.

## Prerequisites

1. Python 3.7+
1. A supported smart trainer (see below)
1. A Windows PC
    * Controller "disabling" is hacky right now and only implemented for Windows

## Support

_Currently only support 1 smart trainer. Will need contributions and testing from community to add support for others. (I can't afford to buy them all)_

1. Wahoo Kickr SNAP

## Tested games

1. Halo Reach from the Master Chief Collection

## Tested controllers

1. XBox 360 Controller connected to PC with the USB XBox 360 Wireless dongle thing.

## Setup

1. Clone repo
1. Run `pip install -r requirements.txt`
1. Run `python motivation.py -h`

### Usage

```
usage: Wahoo Gaming [-h] [-d] [-t TIMEOUT] -p POWER_THRESHOLD

Wahoo Kickr Gaming Motivation App

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debugging
  -t TIMEOUT, --timeout TIMEOUT
                        Connection timeout
  -p POWER_THRESHOLD, --power-threshold POWER_THRESHOLD
                        Under this value you can't play games
```

### Example

* `python motivation.py -t 10 -p 150`
    * Wait 10 seconds for pairing and only enable controller at or above 150 Watt power output.
    * Press `cntrl-c` to quit. Make sure to only hit it once so it can cleanup the notification handlers.

__Output__

```
Looking for compatible devices...
Found device:  KICKR SNAP 84AA
        Address:  D5:E3:1D:29:6F:55
        Details:  Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementReceivedEventArgs
        Metadata:  {'uuids': ['00001818-0000-1000-8000-00805f9b34fb'], 'manufacturer_data': {}}
Found device:  Unknown
        Address:  AC:9E:17:F2:15:5C
        Details:  Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementReceivedEventArgs
        Metadata:  {'uuids': ['cbbfe0e1-f7f3-4206-84e0-84cbb3d09dfc'], 'manufacturer_data': {}}

Choose your device:
        0. Rescan
        1. KICKR SNAP 84AA
        2. Unknown

Which device? 1
Choice: KICKR SNAP 84AA
Connecting...
Connected! Parsing services...

[Service] 00001800-0000-1000-8000-00805f9b34fb: Generic Access Profile
        [Char] 00002a00-0000-1000-8000-00805f9b34fb: (read,write) | Name: , Value: b'KICKR SNAP 84AA'
        [Char] 00002a01-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'\x84\x04'
        [Char] 00002a04-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'P\x00\xa0\x00\x00\x00X\x02'
        [Char] 00002aa6-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'\x01'

[Service] 00001801-0000-1000-8000-00805f9b34fb: Generic Attribute Profile
        [Char] 00002a05-0000-1000-8000-00805f9b34fb: (indicate) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 13) | Value: b'\x02\x00'

[Service] 0000180f-0000-1000-8000-00805f9b34fb: Battery Service
        [Char] 00002a19-0000-1000-8000-00805f9b34fb: (read,notify) | Name: , Value: b'd'
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 17) | Value: b'\x00\x00'

[Service] 0000180a-0000-1000-8000-00805f9b34fb: Device Information
        [Char] 00002a29-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'Wahoo Fitness'
        [Char] 00002a25-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'18TR30330962'
        [Char] 00002a27-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'4'
        [Char] 00002a26-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'2.3.63'

[Service] a026ee01-0a7d-4ab3-97fa-f1500f9feb8b: Unknown
        [Char] a026e002-0a7d-4ab3-97fa-f1500f9feb8b: (write-without-response,notify) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 30) | Value: b'\x00\x00'
        [Char] a026e004-0a7d-4ab3-97fa-f1500f9feb8b: (notify) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 33) | Value: b'\x00\x00'

[Service] a026ee03-0a7d-4ab3-97fa-f1500f9feb8b: Unknown
        [Char] a026e00a-0a7d-4ab3-97fa-f1500f9feb8b: (write-without-response,notify) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 37) | Value: b'\x00\x00'

[Service] 00001818-0000-1000-8000-00805f9b34fb: Cycling Power
        [Char] 00002a63-0000-1000-8000-00805f9b34fb: (notify) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 41) | Value: b'\x00\x00'
        [Char] 00002a65-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'\x06\x12'
        [Char] 00002a5d-0000-1000-8000-00805f9b34fb: (read) | Name: , Value: b'\x00'
        [Char] a026e005-0a7d-4ab3-97fa-f1500f9feb8b: (write,indicate) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 48) | Value: b'\x00\x00'
        [Char] 00002a66-0000-1000-8000-00805f9b34fb: (write,indicate) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 51) | Value: b'\x00\x00'

[Service] a026ee0b-0a7d-4ab3-97fa-f1500f9feb8b: Unknown
        [Char] a026e037-0a7d-4ab3-97fa-f1500f9feb8b: (read,write-without-response,notify) | Name: , Value: b''
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 55) | Value: b'\x00\x00'

[Service] a026ee06-0a7d-4ab3-97fa-f1500f9feb8b: Unknown
        [Char] a026e023-0a7d-4ab3-97fa-f1500f9feb8b: (write-without-response,notify) | Name: , Value: None
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 59) | Value: b'\x00\x00'

Enabling notifications for service Battery Service
Enabling notifications for service Unknown
Enabling notifications for service Unknown
Enabling notifications for service Cycling Power
Enabling notifications for service Unknown
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Power: 0w
Enabling notifications for service Unknown
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Listening for notifications. Cntrl-C to exit...
Power: 0w
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Power: 0w
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Power: 0w
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Power: 0w
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
YOU'RE DOING BAD!!
Clean exit...
Stopping notifications. Please wait (don't hit cntrl-c again dummy, we're working on it)...
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Power: 0w
Cycling Power: 14 00 00 00 18 E5 8D 0A 00 00 3A F0
Power: 0w
Done!
```

Happy peddling.
