from dataclasses import dataclass
from enum import Enum
from src.application.client import ClientPool
from src.application.analytics import ChannelRelevanceEstimator
from src.infrastructure.logging import logger
from src.infrastructure.storage import Storage, StoredItem
from src.infrastructure.telegram import MessageResponse
from .search import Search


class ChannelItemStatus(Enum):
    RELEVANCE_UNKNOWN = 1
    QUEUED_FOR_ANCESTORS_SEARCH = 2
    FINISHED = 3


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

    def __init__(self, 
                 client_pool: ClientPool, 
                 storage: Storage,
                 relevance_estimator: ChannelRelevanceEstimator, 
                 start_channels: list[str],
                 max_channels_count: int,
                 number_of_messages_for_ancestor_search: int
                 ):
        self._client_pool = client_pool
        self._storage = storage
        self._relevance_estimator = relevance_estimator
        self._max_channels_count = max_channels_count
        self._number_of_messages_for_ancestor_search = number_of_messages_for_ancestor_search
        for x in start_channels:
            self._enqueue_channel(x)

    def _enqueue_channel(self, channel_id: str):
        logger.info(f'Found new channel: {channel_id}')
        channel = ChannelItem(channel_id, None, ChannelItemStatus.RELEVANCE_UNKNOWN)
        self._channels[channel_id] = channel
        self._storage.save(StoredChannelItem(channel))

    async def start(self):
        i = 0
        while not self._is_finished():
            logger.info(f'Step {i}. Total number of chanels: {len(self._channels)}')
            await self._update_relevance()
            await self._search_ancestors()
            i += 1
        logger.info(f'Step {i}. Total number of chanels: {len(self._channels)}')
        # TODO Should not return the whole list. 
        # Should either yield row-by-row or save directly to storage. 
        return self._channels 
            
    async def _update_relevance(self):
        logger.info('Updating relevance...')
        channels = [x for x in self._channels.values() if x.status==ChannelItemStatus.RELEVANCE_UNKNOWN]
        for channel in channels:
            channel.relevance = await self._relevance_estimator.get_relevance(channel.channel_id)
            channel.status = ChannelItemStatus.QUEUED_FOR_ANCESTORS_SEARCH
            self._storage.save(StoredChannelItem(channel))

    async def _search_ancestors(self):
        logger.info('Searching ancestors...')
        next_channel = None
        max_relevance = -1
        for channel in self._channels.values():
            if channel.status != ChannelItemStatus.QUEUED_FOR_ANCESTORS_SEARCH:
                continue
            if channel.relevance > max_relevance:
                max_relevance = channel.relevance
                next_channel = channel
        messages = await self._client_pool.get().get_messages(
            next_channel.channel_id, 
            count=self._number_of_messages_for_ancestor_search
        )
        for m in messages:
            child_channel_id = m.channel_fwd_from_id
            if child_channel_id is None:
                continue
            self._storage.save(StoredChannelLink(next_channel.channel_id, child_channel_id, m))
            self._storage.save(StoredMessage(m))
            if child_channel_id not in self._channels:
                self._enqueue_channel(child_channel_id)
        next_channel.status = ChannelItemStatus.FINISHED
        self._storage.save(StoredChannelItem(next_channel))

    def _is_finished(self):
        if len(self._channels) >= self._max_channels_count:
            return True
        if len([x for x in self._channels.values() if x.status!=ChannelItemStatus.FINISHED]) == 0:
            return True
        return False


class StoredMessage(StoredItem):
    
    def __init__(self, message: MessageResponse):
        self._value = {
            'id': message.message_id,
            'channel_id': message.channel_id,
            'text': message.text,
            'datetime': message.datetime
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
            'id': f'{channel_id}_{message.message_id}',
            'channel_id': channel_id,
            'channel_fwd_from_id': channel_fwd_from_id,
            'message_id': message.message_id,
            'datetime': message.datetime
        }
    
    def get_type(self) -> str:
        return 'channel_link'

    def get_key(self) -> str:
        return 'id'

    def get_value(self) -> dict[str, str]:
        return self._value

    def __str__(self):
        return self.get_type() + '=' + str(self._value)


class StoredChannelItem(StoredItem):
    
    def __init__(self, channel: ChannelItem):
        self._value = {
            'id': channel.channel_id,
            'relevance': channel.relevance,
            'status': channel.status
        }    

    def get_type(self) -> str:
        return 'channel_item'
    
    def get_key(self) -> str:
        return 'id'

    def get_value(self) -> dict[str, str]:
        return self._value

    def __str__(self):
        return self.get_type() + '=' + str(self._value)