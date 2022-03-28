import aiohttp
import logging

logger = logging.getLogger(__name__)

NTRIP_HEADERS = {
        "Ntrip-Version": "Ntrip/2.0",
        "User-Agent": "NTRIP deweederbot/1.0"
}

async def ntrip_client(caster, user, password, mountpoint, port=2101):
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(user, password), headers=NTRIP_HEADERS) as session:
        response = await session.get(f"http://{caster}:{port}/{mountpoint}")

        async for data in response.content.iter_any():
            logger.info(f"Got NTRIP DATA: {len(data)}")