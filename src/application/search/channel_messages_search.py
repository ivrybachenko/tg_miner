import asyncio
import pytz
from datetime import datetime
from abc import ABC, abstractmethod
from src.application.client import ClientPool
from src.infrastructure.storage import Storage, StoredItem
from src.infrastructure.telegram import MessageResponse
from src.infrastructure.logging import logger
from .search import Search


class MessageFilter(ABC):
    @abstractmethod
    def match(self, message: MessageResponse) -> bool:
        pass


class AllMessageFilter(MessageFilter):
    def match(self, message: MessageResponse) -> bool:
        return True


class KeywordMessageFilter(MessageFilter):

    _keywords = []

    def __init__(self, keywords: list[str]):
        self._keywords = [x.lower() for x in keywords]

    def match(self, message: MessageResponse) -> bool:
        if message.text is None:
            return False
        text_lower = message.text.lower()
        for kw in self._keywords:
            if kw in text_lower:
                return True
        return False


class ChannelMessagesSearch(Search):
    """
    Downloads messages from Telegram channel.
    """
    _client_pool: ClientPool = None
    _storage: Storage = None
    _channel_id: str = None
    _max_message_count: int = None
    _message_batch_size: int = 0
    _filter: MessageFilter = None
    _min_date: datetime = None
    _max_date: datetime = None
    _start_message_id: int = None

    def __init__(self, 
                 client_pool: ClientPool, 
                 storage: Storage, 
                 channel_id: str, 
                 max_message_count: int,
                 message_batch_size: int,
                 min_date: str,
                 max_date: str,
                 filter: MessageFilter = AllMessageFilter(),
                ):
        self._client_pool = client_pool
        self._storage = storage
        self._channel_id = channel_id
        self._max_message_count = max_message_count
        self._message_batch_size = message_batch_size
        self._filter = filter
        self._min_date = datetime.strptime(min_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        self._max_date = datetime.strptime(max_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        self._start_message_id = self._read_state()['offset_id']
        logger.info(f'Resume from message with id {self._start_message_id}')

    def _read_state(self):
        messages = self._storage.read('message')
        if messages is None:
            return {
                'offset_id': 0
            }
        messages = messages.split('\n')
        message_ids = [v.split('\t')[0] for v in messages][1:-1]
        message_ids = [int(x) for x in message_ids]
        min_message_id = message_ids[0]
        for id in message_ids:
            min_message_id = min(min_message_id, id)
        return {
            'offset_id': min_message_id
        }

    async def start(self):
        if self._client_pool.get_size() == 0:
            raise Exception('Pool has no active clients. Unable to run search.')
        offset_id=self._start_message_id
        total_messages=0
        while True:
            logger.info(f'Total messages: {total_messages}')
            try:
                results = await asyncio.gather(
                    *[
                        self._download_batch(self._message_batch_size, offset_id, i*self._message_batch_size)
                        for i in range(self._client_pool.get_size())
                    ]
                )
            except Exception as e:
                logger.error(e)
            results = [x for x in results if x is not None]
            if len(results) == 0: 
                # TODO
                # If all results are ERROR than they probably could be retried
                # But currently it leads to finishing the search
                logger.info('No results found.')
                return
            should_finish = False
            for result in results: 
                logger.info('Result size is ' + str(result['size']))
                total_messages += result['size']
                if result['size'] != 0:
                    if offset_id == 0:
                        offset_id = result['last_message_id']
                    offset_id = min(offset_id, result['last_message_id'])
                if result['size'] == 0 or total_messages>=self._max_message_count:
                    should_finish = True
            if should_finish:
                return
    
    async def _download_batch(self, batch_size, offset_id, add_offset):
        if offset_id == 0 and add_offset != 0:
            # We don't want to get the first batch multiple times
            return None
        try:
            messages = await self._client_pool.get().get_messages(
                self._channel_id, 
                limit=batch_size,
                offset_id=offset_id,
                add_offset=add_offset,
                offset_date=self._max_date
            )
            messages = [m for m in messages if m.datetime >= self._min_date]
            if len(messages) == 0:
                return {
                    'last_message_id': None,
                    'size': len(messages)
                }
            stats = {
                'last_message_id': messages[-1].message_id,
                'size': len(messages)
            }
            messages = [m for m in messages if self._filter.match(m)]
            messages = [m for m in messages if m.text is not None]
            messages = [m for m in messages if m.datetime <= self._max_date]
            for message in messages:
                message.text = message.text.replace('\n', r'\n')
                self._storage.save(StoredMessage(message))
            return stats
        except Exception as e:
            logger.error(e)
            self._storage.save(StoredGetMessageError(
                self._channel_id,
                batch_size, 
                offset_id,
                add_offset,
                e
            ))
            return None


class StoredMessage(StoredItem):
    
    def __init__(self, message: MessageResponse|dict[str,str]):
        if isinstance(message, MessageResponse):
            self._value = {
                'message_id': message.message_id,
                'channel_id': message.channel_id,
                'channel_from_id': message.channel_fwd_from_id,
                'date': message.datetime,
                'views_count': message.views,
                'forwards_count': message.forwards,
                'reactions': message.reactions,
                'replies_count': message.replies_count,
                'text': message.text,
            }
        elif isinstance(message, dict):
            self._value = {
                'message_id': message.get('id', None),
                'channel_id': message.get('channel_id', None),
                'text': message.get('text', None)
            }

    def get_type(self) -> str:
        return 'message'
        
    def get_value(self) -> dict[str, str]:
        return self._value
    
    def __eq__(self, other):
        if isinstance(other, StoredMessage):
            return self._value == other._value
        return False
    
    def __str__(self):
        return self.get_type() + '=' + str(self._value)


class StoredGetMessageError(StoredItem):
    
    def __init__(self, channel_id, limit, offset_id, add_offset, ex):
        self._value = {
            'channel_id': str(channel_id),
            'limit': str(limit),
            'offset_id': str(offset_id),
            'add_offset': str(add_offset),
            'exception': str(ex)
        }

    def get_type(self) -> str:
        return 'get_message_error'
        
    def get_value(self) -> dict[str, str]:
        return self._value
    
    def __eq__(self, other):
        if isinstance(other, StoredGetMessageError):
            return self._value == other._value
        return False
    
    def __str__(self):
        return self.get_type() + '=' + str(self._value)