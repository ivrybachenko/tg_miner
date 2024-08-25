from dataclasses import dataclass
from enum import Enum
from src.application.client import ClientPool
from src.application.analytics import ChannelRelevanceEstimator
from src.infrastructure.logging import logger

class ChannelItemStatus(Enum):
    RELEVANCE_UNKNOWN = 1
    QUEUED_FOR_ANCESTORS_SEARCH = 2
    FINISHED = 3


@dataclass
class ChannelItem:
    channel_id: str
    relevance: int
    status: ChannelItemStatus


class SnowballChannelSearch:
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
    _relevance_estimator = None
    _channels: dict[str, ChannelItem] = {}
    _max_channels_count = None
    _number_of_messages_for_ancestor_search = None

    def __init__(self, 
                 client_pool: ClientPool, 
                 relevance_estimator: ChannelRelevanceEstimator, 
                 start_channels: list[str],
                 max_channels_count: int,
                 number_of_messages_for_ancestor_search: int
                 ):
        self._client_pool = client_pool
        self._relevance_estimator = relevance_estimator
        self._max_channels_count = max_channels_count
        self._number_of_messages_for_ancestor_search = number_of_messages_for_ancestor_search
        for x in start_channels:
            self._enqueue_channel(x)

    def _enqueue_channel(self, channel_id: str):
        logger.info(f'added channel {channel_id}')
        self._channels[channel_id] = ChannelItem(channel_id, None, ChannelItemStatus.RELEVANCE_UNKNOWN)

    async def start(self):
        i = 0
        while not self._is_finished():
            logger.info(f'Step {i}. Result: {self._channels}')
            await self._update_relevance()
            await self._search_ancestors()
            i += 1
        logger.info(f'Step {i}. Result: {self._channels}')
        return self._channels
            
    async def _update_relevance(self):
        logger.info('Updating relevance...')
        channels = [x for x in self._channels.values() if x.status==ChannelItemStatus.RELEVANCE_UNKNOWN]
        for channel in channels:
            channel.relevance = await self._relevance_estimator.get_relevance(channel.channel_id)
            channel.status = ChannelItemStatus.QUEUED_FOR_ANCESTORS_SEARCH

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
            if child_channel_id not in self._channels:
                self._enqueue_channel(child_channel_id)
        next_channel.status = ChannelItemStatus.FINISHED

    def _is_finished(self):
        if len(self._channels) >= self._max_channels_count:
            return True
        if len([x for x in self._channels.values() if x.status!=ChannelItemStatus.FINISHED]) == 0:
            return True
        return False
