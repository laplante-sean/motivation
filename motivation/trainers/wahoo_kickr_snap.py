'''
Code to handle the Wahoo Kickr SNAP
'''
import struct
from motivation.trainers import SmartTrainer


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


class WahooKickrSnap(SmartTrainer):
    '''
    Specific implementation to handle the Wahoo Kickr SNAP
    '''

    DEVICE_UUID = "00001818-0000-1000-8000-00805f9b34fb"

    def __init__(self, power_tracker, client):
        super().__init__(power_tracker, client)

    def notification_handler(self, sender, data):
        '''
        Simple notification handler which prints the data received.
        '''
        service_desc = self.client.NOTIF_LOOKUP.get(sender, "Unknown Service")
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
                    self.power_tracker.set_power(vals[2])
                    print(f"Power: {self.power_tracker.get_effective_power()}w")

