from src.infrastructure.logging import logger
from .storage import Storage, StoredItem


class ConsoleStorage(Storage):

    def save(self, item: StoredItem):
        logger.info(f'Saved {item}')