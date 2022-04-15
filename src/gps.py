import asyncio
import logging
from typing import Tuple
import numpy as np
import time
import struct

from periphery import Serial

from ubxtranslator.core import Parser, Cls
from ubxtranslator.predefined import NAV_CLS, ACK_CLS

logger = logging.getLogger(__name__)

# Class message values
ack_ms= {
    'ACK':0x01, 'NAK':0x00
}
cfg_ms= {
    'OTP':0x41,    'PIO':0x2c,      'PRT':0x00,     'PT2':0x59,     'RST':0x04,
    'SPT':0x64,    'USBTEST':0x58,  'VALDEL':0x8c,  'VALGET':0x8b,
    'VALSET':0x8a
}
esf_ms= {
    'ALG':0x14,       'INS':0x15,    'MEAS':0x02,  'RAW':0x03,
    'RESETALG':0x13,  'STATUS':0x10
}
inf_ms= {
    'DEBUG':0x04,  'ERROR':0x00,   'NOTICE':0x02,
    'TEST':0x03,   'WARNING':0x01
}
mga_ms= {
    'ACK':0x60,       'BDS_EPH':0x03,
    'BDS_ALM':0x03,   'BDS_HEALTH':0x03,      'BDS_UTC':0x03,
    'DBD_POLL':0x80,  'DBD_IO':0x80,          'GAL_EPH':0x02,
    'GAL_ALM':0x02,   'GAL_TIMEOFFSET':0x02,  'GAL_UTC':0x02
}
mon_ms= {
    'COMMS':0x36,  'GNSS':0x28,  'HW3':0x37,  'PATCH':0x27,
    'PIO':0x24,    'PT2':0x2b,   'RF':0x38,   'RXR':0x21,
    'SPT':0x2f
}
nav_ms= {
    'ATT':0x05,        'CLOCK':0x22,     'COV':0x36,
    'DOP':0x04,        'EELL':0x3d,      'EOE':0x61,        'GEOFENCE':0x39,
    'HPPOSECEF':0x13,  'HPPOSLLH':0x14,  'ORB':0x34,        'POSECEF':0x01,
    'POSLLH':0x02,     'PVT':0x07,       'RELPOSNED':0x3c,  'SAT':0x35,
    'SBAS':0x32,       'SIG':0x43,       'STATUS':0x03,     'TIMBDS':0x24,
    'TIMEGAL':0x25,    'TIMEGLO':0x23,   'TIMEGPS':0x20,    'TIMELS':0x25,
    'TIMEQZSS':0x27,   'TIMEUTC':0x21,   'VELECEF':0x11,    'VELNED':0x12
}
time_ms= {
    'TM2':0x03, 'TP':0x01, 'VRFY':0x06
}

class GPS:
    def __init__(self, serial_port="/dev/ttyACM0", baudrate=38400) -> None:
        self.port = Serial(serial_port, baudrate=baudrate)
        
    async def setup(self):
        self.queue = asyncio.Queue()

    def send_message(self, ubx_class, ubx_id, ubx_payload = None):
        """
        From https://github.com/sparkfun/Qwiic_Ublox_Gps_Py/blob/d7c054520982bf3571359157ed916d2ff1cc8eb3/ublox_gps/ublox_gps.py#L123
        Sends a ublox message to the ublox module.
        :param ubx_class:   The ublox class with which to send or receive the
                            message to/from.
        :param ubx_id:      The message id under the ublox class with which
                            to send or receive the message to/from.
        :param ubx_payload: The payload to send to the class/id specified. If
                            none is given than a "poll request" is
                            initiated.
        :return: True on completion
        :rtype: boolean
        """

        SYNC_CHAR1 = 0xB5
        SYNC_CHAR2 = 0x62

        if ubx_payload == b'\x00' or ubx_payload is None:
            payload_length = 0
        elif type(ubx_payload) is not bytes:
            ubx_payload = bytes([ubx_payload])
            payload_length = len(ubx_payload)
        else:
            payload_length = len(ubx_payload)

        if payload_length > 0:
            message = struct.pack('BBBBBB', SYNC_CHAR1, SYNC_CHAR2,
                                  ubx_class.id_, ubx_id, (payload_length & 0xFF),
                                  (payload_length >> 8)) + ubx_payload

        else:
            message = struct.pack('BBBBBB', SYNC_CHAR1, SYNC_CHAR2,
                                  ubx_class.id_, ubx_id, (payload_length & 0xFF),
                                  (payload_length >> 8))

        checksum = Parser._generate_fletcher_checksum(message[2:])

        self.port.write(message + checksum)

        return True

    async def check_nav_each_second(self):
        while True:
            await self.queue.put((NAV_CLS, nav_ms.get('PVT')))
            await asyncio.sleep(1.0)

    async def run(self):
        parser = Parser([NAV_CLS, ACK_CLS])

        asyncio.create_task(self.check_nav_each_second())

        try:
            # Send all pending messages
            while True:
                try:
                    message = await self.queue.get()

                    if type(message) is tuple:
                        ubx_class, ubx_id = message
                        self.send_message(ubx_class, ubx_id)
                        msg = parser.receive_from(self.port)
                        logger.info(msg)
                    else:
                        logger.info(f"GPS got RTCM Message {len(message)}")
                        self.port.write(message)
                except asyncio.QueueEmpty:
                    break
                except asyncio.TimeoutError:
                    break

        except (ValueError, IOError) as err:
            logger.exception("GPS Error")
            

