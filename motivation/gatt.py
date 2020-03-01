'''
GATT Classes
'''


class GATTUnsupportedOperation(Exception):
    pass


class GATTFailedToNotify(Exception):
    pass


class GATTDevice:
    '''
    Class that represents a GATT BLE device
    '''

    def __init__(self, uuid, device):
        self.uuid = uuid
        self.address = device.address
        self.name = device.name
        self.details = device.details
        self.metadata = device.metadata
        self.device = device

    def __str__(self):
        return f"[Device] {self.name}" + "\n\t".join([
            f"Address: {self.address}",
            f"Details: {self.details}",
            f"Metadata: {self.metadata}"
        ])


class GATTDescriptor:
    '''
    Class that represents a GATT service characterisitc descriptor
    '''

    def __init__(self, client, descriptor):
        self.client = client
        self.descriptor = descriptor
        self.uuid = descriptor.uuid
        self.value = None
        self.error = None

    def __str__(self):
        return f"[Descriptor] {self.uuid}: (Handle: {self.descriptor.handle}) | Value: {self.value or self.error}"

    async def read(self):
        try:
            self.value = bytes(await self.client.read_gatt_descriptor(self.descriptor.handle))
        except Exception as e:
            self.value = None
            self.error = f"Failed to read descriptor {self.uuid}: {e}"

        return self.value

    async def parse(self):
        await self.read()  # Ignore return. We just want to populate the initial value


class GATTCharacteristic:
    '''
    Class that represents a GATT service characteristic
    '''

    def __init__(self, client, characteristic):
        self.client = client
        self.characteristic = characteristic
        self.uuid = characteristic.uuid
        self.descriptors = []
        self.value = None
        self.error = None

    def __str__(self):
        return f"[Char] {self.uuid}: ({','.join(self.characteristic.properties)}) | Name: {self.characteristic.description}, Value: {self.value or self.error}"

    def is_read(self):
        return "read" in self.characteristic.properties

    def is_write(self):
        return "write" in self.characteristic.properties or "write-without-response" in self.characteristic.properties

    def is_notify(self):
        return "notify" in self.characteristic.properties

    async def read(self):
        if not self.is_read():
            raise GATTUnsupportedOperation()

        try:
            self.value = bytes(await self.client.read_gatt_char(self.uuid))
        except Exception as e:
            self.value = None
            self.error = f"Failed to read from characteristic {self.uuid}: {e}"

        return self.value

    async def notify(self, handler):
        if not self.is_notify():
            raise GATTUnsupportedOperation()

        try:
            await self.client.start_notify(self.uuid, handler)
        except Exception as e:
            raise GATTFailedToNotify(f"Could not enable notifications for {self.uuid}: {e}")

    async def stop_notify(self):
        if not self.is_notify():
            raise GATTUnsupportedOperation()

        try:
            await self.client.stop_notify(self.uuid)
        except Exception as e:
            raise GATTFailedToNotify(f"Coult not disable notifications for {self.uuid}: {e}")

    async def parse(self):
        if self.is_read():
            await self.read()  # Ignore return. We just want to populate the initial value

        for descriptor in self.characteristic.descriptors:
            gatt_desc = GATTDescriptor(self.client, descriptor)
            await gatt_desc.parse()
            self.descriptors.append(gatt_desc)


class GATTService:
    '''
    Class that represents a GATT service
    '''

    def __init__(self, client, service):
        self.client = client
        self.uuid = service.uuid
        self.description = service.description
        self.service = service
        self.characteristics = []

    def get_characteristic(self, uuid):
        for char in self.characteristics:
            if char.uuid == uuid:
                return char
        return None

    async def notify(self, handler):
        for char in self.characteristics:
            if char.is_notify():
                await char.notify(handler)

    async def stop_notify(self):
        for char in self.characteristics:
            if char.is_notify():
                await char.stop_notify()

    async def parse(self):
        '''
        Parse out the service characteristics
        '''
        for char in self.service.characteristics:
            gatt_char = GATTCharacteristic(self.client, char)
            await gatt_char.parse()
            self.characteristics.append(gatt_char)

    def __str__(self):
        return f"[Service] {self.uuid}: {self.description}"

    def print_service(self):
        service_str = str(self) + "\n"

        for char in self.characteristics:
            service_str += "\t" + str(char) + "\n"

            for desc in char.descriptors:
                service_str += "\t\t" + str(desc) + "\n"

        return service_str
