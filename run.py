import asyncio
from src.application.analytics import ChannelRelevanceEstimator
from src.application.client import ClientPool
from src.application.client import ClientFactory
from src.application.search import SnowballChannelSearch
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

    search = SnowballChannelSearch(
        client_pool=client_pool, 
        relevance_estimator=ChannelRelevanceEstimator(),
        start_channels=['cb_economics'],
        max_channels_count=10,
        number_of_messages_for_ancestor_search=10
    )
    channels = await search.start()
    logger.info('Search finished.')
    logger.info(f'Search result is {channels}')
    # channel = await client_pool.get().get_channel('cb_economics')
    # logger.info(channel)Agitblog
    # storage.save_channel(channel)
    # channel = await client_pool.get().get_channel('economica')
    # storage.save_channel(channel)
    # messages = await client_pool.get().get_messages('cb_economics')
    # for m in messages:
    #     storage.save_message(m)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())