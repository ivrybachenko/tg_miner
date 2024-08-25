import asyncio
from src.application.client import ClientPool
from src.application.client import ClientFactory
from src.infrastructure.storage import CsvStorage
from src.infrastructure.logging import logger

async def main():
    """
    Application entrypoint. 
    """
    storage = CsvStorage('out')
    client_pool = ClientPool()
    client_factory = ClientFactory()
    for client in client_factory.read_clients_from_properties('properties/clients.properties'):
        client_pool.add_client(client)
    await client_pool.activate_clients()
    logger.info('Application is ready.')

    channel = await client_pool.get().get_channel('cb_economics')
    storage.save_channel(channel)
    channel = await client_pool.get().get_channel('economica')
    storage.save_channel(channel)
    messages = await client_pool.get().get_messages('cb_economics')
    for m in messages:
        storage.save_message(m)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())