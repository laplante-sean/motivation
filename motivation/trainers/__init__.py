'''
Defines the base class for a smart trainer
'''
import os


class SmartTrainer:
    '''
    Base class for a smart trainer. Sub-classes must implement
    some functionality
    '''

    #: The device UUID used to identify which plugin to use
    #: for the devices discovered. This must be set by subclasses
    DEVICE_UUID = None

    def __init__(self, power_tracker, client):
        self.power_tracker = power_tracker
        self.client = client

    def notification_handler(self, sender, data):
        raise NotImplementedError
