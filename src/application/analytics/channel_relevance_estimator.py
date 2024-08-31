from src.application.client import ClientPool
from src.infrastructure.logging import logger


class ChannelRelevanceEstimator:
    async def get_relevance(self, channel_id: str):
        return 0


class KeywordChannelRelevanceEstimator(ChannelRelevanceEstimator):

    _client_pool: ClientPool
    _keywords: dict[str, int]

    def __init__(self, client_pool: ClientPool, keywords: dict[str, int]):
        self._client_pool =client_pool
        self._keywords = keywords

    async def get_relevance(self, channel_id: str):
        try: 
            messages = await self._client_pool.get().get_messages(
                channel_id, 
                limit=100, 
                offset_id=0, 
                add_offset=0
            )
            cnt = 0
            for m in messages:
                if m.text is None:
                    continue
                text = m.text.lower()
                relevance_msg = 1
                for kw, cost in self._keywords.items():
                    if kw in text:
                        # Multiply keywords inside message.
                        # Message with lot of keywords will get high relevance.
                        relevance_msg *= cost 
                if relevance_msg == 1:
                    relevance_msg = 0
                cnt += relevance_msg
            return cnt
        except Exception as e:
            logger.error('Relevance estimation failed. ' + str(e))
            return 0