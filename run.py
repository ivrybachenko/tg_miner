import asyncio
from src.client import ClientPool
from src.storage import CsvStorage
from src.logger import logger

async def main():
    """
    Application entrypoint. 
    """
    storage = CsvStorage('out')
    clientPool = ClientPool()
    clientPool.read_clients_from_properties('properties/clients.properties')
    await clientPool.activate_clients()
    logger.info('Application is ready.')

    client = clientPool.get()
    channel = await client.get_channel('cb_economics')
    storage.save_channel(channel)
    channel = await client.get_channel('economica')
    storage.save_channel(channel)
    messages = await client.get_messages('cb_economics')
    for m in messages:
        storage.save_message(m)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())