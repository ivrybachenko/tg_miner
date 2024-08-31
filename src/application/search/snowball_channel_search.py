import asyncio
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from src.application.client import ClientPool
from src.application.analytics import ChannelRelevanceEstimator
from src.infrastructure.logging import logger
from src.infrastructure.storage import Storage, StoredItem
from src.infrastructure.telegram import MessageResponse, ChannelResponse
from .search import Search


class ChannelItemStatus(Enum):
    QUEUED_FOR_LOADING = 0
    RELEVANCE_UNKNOWN = 1
    QUEUED_FOR_ANCESTORS_SEARCH = 2
    FINISHED = 3
    ERROR = 4


@dataclass
class ChannelItem:
    channel_id: str
    relevance: int
    status: ChannelItemStatus


class SnowballChannelSearch(Search):
    """
    Searches for relevant channels with snowball algorithm.

    Algorithm:
    1. Enqueue start channels.
    1. Estimate the relevance for each enqueued channel.
    2. Pick the most relevant nonprocessed channel. Mark it as processed.
    3. Extract top-k messages from picked channel. 
       If message is forwarded from another channel, enqueue this channel. 
    4. Go to step 2 or finish, if job is done.
    """
    _client_pool = None
    _storage: Storage = None
    _relevance_estimator = None
    _channels: dict[str, ChannelItem] = {}
    _max_channels_count = None
    _number_of_messages_for_ancestor_search = None
    _save_messages = False

    def __init__(self, 
                 client_pool: ClientPool, 
                 storage: Storage,
                 relevance_estimator: ChannelRelevanceEstimator, 
                 start_channels: list[str],
                 max_channels_count: int,
                 number_of_messages_for_ancestor_search: int,
                 save_messages=False
                 ):
        self._client_pool = client_pool
        self._storage = storage
        self._relevance_estimator = relevance_estimator
        self._max_channels_count = max_channels_count
        self._number_of_messages_for_ancestor_search = number_of_messages_for_ancestor_search
        self._save_messages = save_messages
        for x in start_channels:
            self._enqueue_channel(x)

    def _enqueue_channel(self, channel_id: str):
        logger.info(f'Found new channel: {channel_id}')
        channel = ChannelItem(channel_id, None, ChannelItemStatus.QUEUED_FOR_LOADING)
        self._channels[channel_id] = channel
        self._change_status(channel, ChannelItemStatus.RELEVANCE_UNKNOWN)

    def _change_status(self, channel_item: ChannelItem, status: ChannelItemStatus):
        channel_item.status = status
        self._storage.save(StoredChannelItem(channel_item))

    async def start(self):
        if self._client_pool.get_size() == 0:
            raise Exception('Pool has no active clients. Unable to run search.')
        i = 0
        while not self._is_finished():
            logger.info(f'Step {i}. Total number of chanels: {len(self._channels)}')
            await self._load_channels()
            await self._update_relevance()
            await self._search_ancestors()
            i += 1
        logger.info(f'Step {i}. Total number of chanels: {len(self._channels)}')
        # TODO Should not return the whole list. 
        # Should either yield row-by-row or save directly to storage. 
        return self._channels 

    async def _load_channels(self):
        logger.info('Loading titles...')
        channels = [x for x in self._channels.values() if x.status==ChannelItemStatus.QUEUED_FOR_LOADING]
        for channel in channels:
            # Commented because of the bag in MemoryCache
            # try:
            #     channel_response = await self._client_pool.get().get_channel(channel.channel_id)
            # except:
            channel_response = ChannelResponse(
                channel_id=channel.channel_id,
                title=None
            )
            # then I wanted to save channel title into file but currently I do not
            self._change_status(channel, ChannelItemStatus.RELEVANCE_UNKNOWN)

    async def _update_relevance(self):
        logger.info('Updating relevance...')
        channels = [x for x in self._channels.values() if x.status==ChannelItemStatus.RELEVANCE_UNKNOWN]
        for channel in channels:
            channel.relevance = await self._relevance_estimator.get_relevance(channel.channel_id)
            self._change_status(channel, ChannelItemStatus.QUEUED_FOR_ANCESTORS_SEARCH)

    async def _search_ancestors(self):
        logger.info('Searching ancestors...')
        next_channels = self._choose_channels_to_search_ancestors(self._client_pool.get_size())
        next_channels = [x for x in next_channels if x is not None]
        await asyncio.gather(
            *[
                self._search_ancestors_in_channel(x) 
                    for x in next_channels if x is not None
            ]
        )

    def _choose_channels_to_search_ancestors(self, count) -> ChannelItem:
        queue = [x for x in self._channels.values() if x.status == ChannelItemStatus.QUEUED_FOR_ANCESTORS_SEARCH]
        return queue[:count]

    async def _search_ancestors_in_channel(self, channel: ChannelItem):
        try:
            messages = await self._client_pool.get().get_messages(
                channel.channel_id, 
                limit=self._number_of_messages_for_ancestor_search,
                offset_id=0,
                add_offset=0
            )
            for m in messages:
                child_channel_id = m.channel_fwd_from_id
                if child_channel_id is None:
                    continue
                self._storage.save(StoredChannelLink(channel.channel_id, child_channel_id, m))
                if self._save_messages:
                    self._storage.save(StoredMessage(m))
                if child_channel_id not in self._channels:
                    self._enqueue_channel(child_channel_id)
            self._change_status(channel, ChannelItemStatus.FINISHED)
        except Exception as e:
            logger.error(f'Failed to load channel {channel.channel_id}: {e}')
            self._change_status(channel, ChannelItemStatus.ERROR)

    def _is_finished(self):
        if len(self._channels) >= self._max_channels_count:
            return True
        if len([
            x for x in self._channels.values() 
            if x.status!=ChannelItemStatus.FINISHED and x.status!=ChannelItemStatus.ERROR
        ]) == 0:
            return True
        return False


class StoredMessage(StoredItem):
    
    def __init__(self, message: MessageResponse):
        self._value = {
            'message_id': message.message_id,
            'channel_id': message.channel_id,
            'text': message.text,
            'message_datetime': message.datetime
        }    

    def get_type(self) -> str:
        return 'message'

    def get_key(self) -> str:
        return 'id'

    def get_value(self) -> dict[str, str]:
        return self._value

    def __str__(self):
        return self.get_type() + '=' + str(self._value)


class StoredChannelLink(StoredItem):
    
    def __init__(self, channel_id: str, channel_fwd_from_id: str, message: MessageResponse):
        self._value = {
            'channel_id': channel_id,
            'channel_fwd_from_id': channel_fwd_from_id,
            'message_id': message.message_id,
            'message_datetime': message.datetime
        }
    
    def get_type(self) -> str:
        return 'channel_link'

    def get_value(self) -> dict[str, str]:
        return self._value

    def __str__(self):
        return self.get_type() + '=' + str(self._value)


class StoredChannelItem(StoredItem):
    
    def __init__(self, channel: ChannelItem):
        self._value = {
            'channel_id': channel.channel_id,
            'datetime': datetime.now()
        }
        self._channel_status = channel.status
        if channel.status == ChannelItemStatus.QUEUED_FOR_ANCESTORS_SEARCH:
            self._value['relevance'] = channel.relevance

    def get_type(self) -> str:
        return f'channel_{self._channel_status.name}'

    def get_value(self) -> dict[str, str]:
        return self._value

    def __str__(self):
        return self.get_type() + '=' + str(self._value)


class StoredChannel(StoredItem):
    
    def __init__(self, channel: ChannelResponse):
        self._value = {
            'channel_id': channel.channel_id,
            'title': channel.title
        }    

    def get_type(self) -> str:
        return 'channel'

    def get_value(self) -> dict[str, str]:
        return self._value

    def __str__(self):
        return self.get_type() + '=' + str(self._value)