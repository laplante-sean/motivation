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
from motivation.gatt import GATTDevice, GATTCharacteristic, GATTDescriptor, GATTService


class BLEClientConnectionFailed(Exception):
    pass


class UnsupportedTrainer(Exception):
    pass


class BLEClient:
    '''
    Acts as a client. Connects to a server, subscribes to events, etc...
    '''

    def __init__(self, device, power_tracker, timeout=10, debug=False):
        self.device = device
        self.timeout = timeout
        self.power_tracker = power_tracker
        self.debug = debug
        self.loop = asyncio.get_event_loop()
        self.services = []

        # Technically this is a list, but we only care about the first UUID maybe?
        try:
            uuid = self.device.metadata.get("uuids", [])[0]
        except IndexError:
            raise UnsupportedTrainer()

        # Setup the trainer for this client
        loader = TrainerPluginLoader.get()
        trainer_cls = loader.get_by_uuid(uuid)
        if trainer_cls is None:
            raise UnsupportedTrainer()
        self.trainer = trainer_cls(self.power_tracker, self)

    def get_service_with_characteristic(self, char_uuid):
        for service in self.services:
            char = service.get_characteristic(char_uuid)
            if char:
                return service
        return None

    def run(self):
        '''
        Run the client
        '''
        try:
            self.loop.run_until_complete(self._run())
        except BleakError:
            raise BLEClientConnectionFailed()

    async def _run(self):
        '''
        Connect to a chosen device
        '''
        async with BleakClient(self.device.address, loop=self.loop, timeout=self.timeout) as client:
            # Make sure we're connected
            is_connected = await client.is_connected()
            if not is_connected:
                raise BLEClientConnectionFailed()

            # Parse the services and populate self.services
            for service in client.services:
                gatt_service = GATTService(client, service)
                await gatt_service.parse()
                self.services.append(gatt_service)

                # Setup handlers for all notifications
                await gatt_service.notify(self.trainer.notification_handler)

            if self.debug:
                for service in self.services:
                    print(service.print_service())
                    print("")  # For the newline

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

            for service in self.services:
                await service.stop_notify()


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

            uuids = d.metadata.get("uuids", [])
            for uuid in uuids:
                if loader.is_supported_device(uuid):
                    dev = GATTDevice(uuid, d)
                    ret_devices.append(dev)
                    supported = True

                    if self.debug and supported:
                        print(str(dev))
                    break

            if self.debug and not supported:
                print(f"Found unsupported device: {d.name}")

        return ret_devices
