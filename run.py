import asyncio
from src.client_pool import ClientPool
from src.logger import logger

async def main():
    """
    Application entrypoint. 
    """
    clientPool = ClientPool()
    clientPool.read_clients_from_properties('properties/clients.properties')
    await clientPool.activate_clients()
    logger.info('Application is ready.')
    client = clientPool.get()
    channel = await client.get_channel('cb_economics')
    logger.info(channel)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())