import asyncio
from timeit import default_timer as timer
from datetime import timedelta
from src.application.analytics import KeywordChannelRelevanceEstimator
from src.application.client import ClientPool
from src.application.client import ClientFactory
from src.application.search import SnowballChannelSearch, ChannelMessagesSearch, KeywordMessageFilter
from src.infrastructure.storage import TsvStorage, ConsoleStorage
from src.infrastructure.logging import logger

async def main():
    """
    Application entrypoint. 
    """
    storage = TsvStorage('out')
    # storage = ConsoleStorage()
    client_pool = ClientPool()
    client_factory = ClientFactory()
    for client in client_factory.read_clients_from_properties('properties/clients.properties'):
        client_pool.add_client(client)
    await client_pool.activate_clients()
    logger.info('Application is ready.')

    search = ChannelMessagesSearch(
        client_pool = client_pool,
        storage=storage,
        channel_id='legitimniy',
        max_message_count=2,
        message_batch_size=2,
        # filter=KeywordMessageFilter(['траснформ', 'цифров', 'устойчив'])
    )
    start = timer()
    await search.start()
    end = timer()
    logger.info(f'Search finished. Elapsed time: {timedelta(seconds=end-start)}')

    # search = SnowballChannelSearch(
    #     client_pool=client_pool, 
    #     storage=storage,
    #     relevance_estimator=KeywordChannelRelevanceEstimator(
    #         client_pool, 
    #         keywords={
    #             'цифр': 10, 
    #             'трансформ': 10,
    #             'устойчив': 7,
    #             'развити': 5,
    #             'эконом': 5,
    #             'менедж': 5,
    #             'компан': 1
    #         }
    #     ),
    #     start_channels=['cb_economics'],
    #     max_channels_count=10000,
    #     number_of_messages_for_ancestor_search=1000,
    #     save_messages=True
    # )
    # start = timer()
    # await search.start()
    # end = timer()
    # logger.info(f'Search finished. Elapsed time: {timedelta(seconds=end-start)}')
    

loop = asyncio.get_event_loop()
loop.run_until_complete(main())