'''
Handle the bluetooth device specifics
'''
import os
import sys
import time
import asyncio
import argparse
import traceback
import threading

from bleak import BleakClient
from bleak import discover
from bleak.exc import BleakError

from motivation.loader import TrainerPluginLoader
from motivation.controller import disable_controller
from motivation.power import PowerTracker


class BLEClientConnectionFailed(Exception):
    pass


class UnsupportedTrainer(Exception):
    pass


class BLEClient:
    '''
    Acts as a client. Connects to a server, subscribes to events, etc...
    '''
    NOTIFICATION_UUIDS = None
    NOTIF_LOOKUP = None

    def __init__(self, uuid, address, power_tracker, timeout=10, debug=False):
        self.uuid = uuid
        self.address = address
        self.timeout = timeout
        self.power_tracker = power_tracker
        self.debug = debug
        self.loop = asyncio.get_event_loop()

        self.NOTIFICATION_UUIDS = {}
        self.NOTIF_LOOKUP = {}

        loader = TrainerPluginLoader.get()
        trainer_cls = loader.get_by_uuid(self.uuid)
        if trainer_cls is None:
            raise UnsupportedTrainer()
        self.trainer = trainer_cls(self.power_tracker, self)

    def run(self):
        '''
        Run the client
        '''
        self.loop.run_until_complete(self._run())

    async def _run(self):
        '''
        Connect to a chosen device
        '''
        async with BleakClient(self.address, loop=self.loop, timeout=self.timeout) as client:
            is_connected = await client.is_connected()
            if not is_connected:
                raise BLEClientConnectionFailed()

            await self._parse_services(client)

            for val in NOTIFICATION_UUIDS.values():
                if self.debug:
                    print(f"Enabling notifications for service {val['service_description']}")

                for notif in val["notifications"]:
                    try:
                        await client.start_notify(notif, self.trainer.notification_handler)
                    except AttributeError:
                        print(f"Could not enable notifications for {notif}")
                        continue

            try:
                # Run the main loop
                print("Listening for notifications. Cntrl-C to exit...")
                while 1:
                    if not self.power_tracker.pass_fail():
                        #
                        # Hacky code that kindof "disables" the controller...but not really. Just makes it real hard to play
                        #
                        print("YOU'RE DOING BAD!!")
                        disable_controller()

                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Clean exit...")
            except Exception as e:
                print(f"Unhandled exception {e}")

            print("Stopping notifications. Please wait (don't hit cntrl-c again dummy, we're working on it)...")

            for key in NOTIF_LOOKUP.keys():
                await client.stop_notify(key)

    async def _parse_services(self, client):
        '''
        Setup notification handlers for all notification services
        '''
        for service in client.services:
            if self.debug:
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

                if self.debug:
                    print(f"\t[Char] {char.uuid}: ({','.join(char.properties)}) | Name: {char.description}, Value: {value}")

                for descriptor in char.descriptors:
                    value = await client.read_gatt_descriptor(descriptor.handle)

                    if self.debug:
                        print(f"\t\t[Descriptor] {descriptor.uuid}: (Handle: {descriptor.handle}) | Value: {bytes(value)} ")

        if self.debug:
            print("")  # Add a newline for easy readin'


class BLEScanner:
    '''
    Class to handle scanning and connecting to devices
    '''

    def __init__(self, debug=False):
        # Create an event loop
        self.loop = asyncio.get_event_loop()
        self.debug = debug

    def scan(self):
        '''
        Synchronous scan
        '''
        return self.loop.run_until_complete(self._scan())

    async def _scan(self):
        '''
        Scan for Blutooth LE devices
        '''
        ret_devices = []
        loader = TrainerPluginLoader.get()
        devices = await discover()

        for d in devices:
            supported = False

            if self.debug:
                print(f"Found device: {d.name}")
                print(f"\tAddress: {d.address}")
                print(f"\tDetails: {d.details}")
                print(f"\tMetadata: {d.metadata}")

            uuids = d.metadata.get("uuids", [])
            for uuid in uuids:
                if loader.is_supported_device(uuid):
                    ret_devices.append(d)
                    supported = True
                    break

            if self.debug and not supported:
                print(f"Device: {d.name} is not supported.")

        return ret_devices
