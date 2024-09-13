from src.infrastructure.logging import logger
from .client import Client


class ClientPool:
    """
    Responsible for managing a client pool.
    """
    _clients = [] # All registered clients
    _next_client_index = 0 # Id of client which will be used for API call next time

    def add_client(self, client: Client):
        self._clients.append(client)

    def get_size(self):
        return len(self.get_active_clients())

    def get_active_clients(self):
        """
        Returns the list of active clients.
        """
        return [x for x in self._clients if x.is_active]
    
    async def activate_clients(self, fail_on_error: bool = True):
        """
        Ensures that each client is ready for API calls. 
        """
        logger.info('Activating Telegram clients...')
        total_count = len(self._clients)
        for i, client in enumerate(self._clients):
            logger.info(f'Activating Telegram client {i+1}/{total_count}: {client.name}')
            await client.activate()
        count_active = len([x for x in self._clients if x.is_active])
        logger.info('Activating Telegram clients finished.')
        logger.info(f'Successfully activated {count_active} of {total_count} clients.')
        logger.info([
            {
                'name': client.name, 
                'is_active': client.is_active
            } 
            for client in self._clients
        ])
        if count_active != total_count and fail_on_error:
            raise Exception('Not all clients were succesfully activated.')
        
    def get(self) -> Client:
        """
        Returns the next client which can be used for API call.
        """
        active_clients = self.get_active_clients()
        if len(active_clients) == 0:
            raise Exception('No active clients available.')
        next_client = active_clients[self._next_client_index]
        self._next_client_index = (self._next_client_index + 1) % len(active_clients)
        return next_client
