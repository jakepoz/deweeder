import aiohttp
import asyncio
import logging

from typing import ByteString, Tuple

from src.gps import GPS

logger = logging.getLogger(__name__)

NTRIP_HEADERS = {
        "Ntrip-Version": "Ntrip/2.0",
        "User-Agent": "NTRIP deweederbot/1.0"
}

class RTCMParseException(Exception):
    pass

def calc_crc24q(message: bytes) -> int:
    """
    Source: https://github.com/semuconsulting/pyrtcm/blob/main/pyrtcm/rtcmhelpers.py
    Perform CRC24Q cyclic redundancy check.
    If the message includes the appended CRC bytes, the
    function will return 0 if the message is valid.
    If the message excludes the appended CRC bytes, the
    function will return the applicable CRC.
    :param bytes message: message
    :return: CRC or 0
    :rtype: int
    """

    POLY = 0x1864CFB
    crc = 0
    for octet in message:
        crc ^= octet << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= POLY
    return crc & 0xFFFFFF


def parse_rtcm(buf: ByteString) -> Tuple[ByteString, ByteString]:
    """
    Parses a bytearray and decodes RTCM messages one at a time.
    Returns a full RTCM message, plus any remaining buffer to process.

        Ntrip message format
        8 bits - Preamble 0xd3
        6 bits - reserved, usually 0's but could be anything
        10 bits - message length in bytes
        0-1023 bytes
        24 bits - QualComm definition CRC-24Q

    :return (RTCM message, remaining buffer)
    """
    start = 0

    while start < len(buf):
        if buf[start] != 0xd3:
            start += 1
            continue

        if len(buf) < start + 6:
            return None, buf

        msglen = (buf[start + 1] & 0b00000011 > 8) | buf[start + 2] 
        
        if len(buf) < start + 3 + msglen + 3:
            return None, buf

        crc = int.from_bytes(buf[start + 3 + msglen: start + 3 + msglen + 3], "big")

        if calc_crc24q(buf[start: start + 3 + msglen]) == crc:
            return buf[start: start + 3 + msglen + 3], buf[start + 3 + msglen + 3:]
        else:
            logger.warning("CRC Did not match on RTCM packet")
            return None, buf[start + 3 + msglen + 3:]

    return None, bytearray()


class NtripClient:
    def __init__(self, caster:str, user:str, password:str, mountpoint:str, port:int=2101, gps: GPS=None) -> None:
        self.caster = caster
        self.user = user
        self.password = password
        self.mountpoint = mountpoint
        self.port = port
        self.gps = gps

    async def setup(self):
        pass

    async def run(self):
        rtr_buf = bytearray()

        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.user, self.password), headers=NTRIP_HEADERS) as session:
            response = await session.get(f"http://{self.caster}:{self.port}/{self.mountpoint}")
            assert response.status == 200
            logger.warning("Started new Ntrip session")

            async for data in response.content.iter_any():
                logger.info(f"Got NTRIP DATA: {len(data)}, {len(rtr_buf)}")
                rtr_buf += data
                
                #Parse the message stream, and yield only full RTCM messages at a time, to be forwarded along to the GPS module
                while True:
                    rtcm_msg, rtr_buf = parse_rtcm(rtr_buf)

                    if rtcm_msg:
                        await self.gps.queue.put(rtcm_msg)
                    else:
                        break
