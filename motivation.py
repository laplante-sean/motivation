import os
import sys
import time
import struct
import asyncio
import argparse
import traceback
import threading
import win32com.client
from bleak import BleakClient
from bleak import discover
from bleak.exc import BleakError


# Populated by parsing services
NOTIFICATION_UUIDS = {}
NOTIF_LOOKUP = {}

# Best guess...
# From: https://github.com/stuwilkins/antplus/blob/master/lib/antmessage.cpp
#
# I'm making an assumption here that the data is just ANT+ data being sent
# over bluetooth. Something like...
#
# ANT_Message {
#     uint8_t type;
#     uint8_t channel;
#     uint16_t acceleration;
#     uint16_t wut1;  //WUT?
#     uint16_t speed;  //WUT?
#     uint8_t wut2;  //WUT?
#     uint8_t wut3;  //WUT?
# }
#
# Maybe those b0 through b4 things are data. Let's treat it as a UINT32 and
# see what happens...
#
# Example "Cycling Power" data: 14 00 00 00 3A 85 EA 01 00 00 EC 4B
POWER_STRUCT = "BBHHBBHH"
POWER_STRUCT_SIZE = struct.calcsize(POWER_STRUCT)


class PowerTracker:
    '''
    This is probably so wrong...but maybe it'll work?
    '''

    def __init__(self):
        self.lock = threading.Lock()
        self.power = 0
        self.start = 0
        self.start_set = False

    def set_power(self, power):
        '''
        Value directly from device
        '''
        with self.lock:
            self.power = power


    def set_start_power(self, power):
        '''
        Value directly from device
        '''
        with self.lock:
            if self.start_set:
                return
            self.start = power
            self.start_set = True

    def get_effective_power(self):
        '''
        Diff b/w current power and start power
        '''
        with self.lock:
            if self.power < self.start:
                self.start = self.power
                return 0

            return self.power - self.start


shell = win32com.client.Dispatch("WScript.Shell")
tracker = PowerTracker()


def notification_handler(sender, data):
    '''
    Simple notification handler which prints the data received.
    '''
    service_desc = NOTIF_LOOKUP.get(sender, "Unknown Service")
    fmt_data = " ".join("%02x".upper() % b for b in data)
    print(f"{service_desc}: {fmt_data}")

    if "cycling power" in service_desc.lower().strip():
        if len(data) < POWER_STRUCT_SIZE:
            print(f"Not enough data to unpack")
        else:
            try:
                vals = struct.unpack(POWER_STRUCT, data[:POWER_STRUCT_SIZE])
            except Exception as e:
                print(f"Failed to unpack cycling power data: {e}")
            else:
                '''
                for idx, val in enumerate(vals):
                    num = idx + 1
                    print(f"\tVal{num}: {val}")
                '''
                tracker.set_start_power(vals[2])
                tracker.set_power(vals[2])
                print(f"Power: {tracker.get_effective_power()}w")


async def parse_services(client):
    '''
    Dump all services, characteristics, and info
    '''
    for service in client.services:
        print(f"\n[Service] {service.uuid}: {service.description}")
        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = bytes(await client.read_gatt_char(char.uuid))
                except Exception as e:
                    value = str(e).encode()
            else:
                value = None

            if "notify" in char.properties:
                # This is something we can recieve notifications about.
                if service.uuid not in NOTIFICATION_UUIDS:
                    NOTIFICATION_UUIDS[service.uuid] = {
                        "service_description": service.description,
                        "notifications": []
                    }

                NOTIF_LOOKUP[char.uuid] = service.description
                NOTIFICATION_UUIDS[service.uuid]["notifications"].append(char.uuid)

            print(f"\t[Char] {char.uuid}: ({','.join(char.properties)}) | Name: {char.description}, Value: {value}")

            for descriptor in char.descriptors:
                value = await client.read_gatt_descriptor(descriptor.handle)
                print(f"\t\t[Descriptor] {descriptor.uuid}: (Handle: {descriptor.handle}) | Value: {bytes(value)} ")

    print("")  # Add a newline for easy readin'


async def scan():
    '''
    Scan for Blutooth LE devices
    '''
    devices = await discover()
    for d in devices:
        print("Found device: ", d.name)
        print("\tAddress: ", d.address)
        print("\tDetails: ", d.details)
        print("\tMetadata: ", d.metadata)

    return devices


async def run_client(threshold, address, loop, timeout=10, debug=False):
    '''
    Connect to a chosen device
    '''
    print("Connecting...")

    async with BleakClient(address, loop=loop, timeout=timeout) as client:
        is_connected = await client.is_connected()
        if not is_connected:
            print("Failed to connect")
            return False

        print("Connected! Parsing services...")

        await parse_services(client)

        for val in NOTIFICATION_UUIDS.values():
            print(f"Enabling notifications for service {val['service_description']}")
            for notif in val["notifications"]:
                try:
                    await client.start_notify(notif, notification_handler)
                except AttributeError:
                    print(f"Could not enable notifications for {notif}")
                    continue

        try:
            # Run the main loop
            print("Listening for notifications. Cntrl-C to exit...")
            while 1:
                current = tracker.get_effective_power()
                if current < threshold:
                    #
                    # Hacky code that kindof "disables" the controller...but not really. Just makes it real hard to play
                    #
                    print("YOU'RE DOING BAD!!")
                    shell.SendKeys(" ", 0)

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Clean exit...")
        except Exception as e:
            print(f"Unhandled exception {e}")

        print("Stopping notifications. Please wait (don't hit cntrl-c again dummy, we're working on it)...")

        for key in NOTIF_LOOKUP.keys():
            await client.stop_notify(key)

    return True


def main(threshold, debug=False, timeout=10):
    '''
    Entry point
    '''
    os.system("cls")

    # Look for compatible devices
    loop = asyncio.get_event_loop()

    while 1:
        print("Looking for compatible devices...")

        devices = loop.run_until_complete(scan())

        print("\nChoose your device:")
        print("\t0. Rescan")
        for idx, d in enumerate(devices):
            choice = idx + 1
            print(f"\t{choice}. {d.name}")

        choice = input("\nWhich device? ")
        try:
            choice = int(choice)

            if choice > len(devices) or choice < 0:
                raise ValueError("no")
        except ValueError:
            print("Invalid. You're bad at computers.")
            sys.exit(1)

        if choice == 0:
            os.system("cls")
            continue
        break

    choice = devices[choice - 1]
    print(f"Choice: {choice.name}")

    address = choice.address
    success = loop.run_until_complete(run_client(threshold, address, loop, timeout=timeout, debug=debug))
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Wahoo Gaming", description="Wahoo Kickr Gaming Motivation App")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging", required=False)
    parser.add_argument("-t", "--timeout", action="store", type=int, help="Connection timeout", required=False, default=10)
    parser.add_argument("-p", "--power-threshold", action="store", type=int, help="Under this value you can't play games", required=True)
    args = parser.parse_args()

    try:
        main(args.power_threshold, debug=args.debug, timeout=args.timeout)
    except KeyboardInterrupt:
        print("LATER!")
    except BleakError as e:
        print(f"Ya fucked: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unhandled fuck up: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("Done!")
    sys.exit(0)