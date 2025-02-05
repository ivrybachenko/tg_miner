import psycopg2
from .storage import StoredItem, Storage


class PostgresStorage(Storage):
    """
    Stores result into Postgres database.
    """
    _conn = None
    _total_count = {}

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._conn = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
        self._conn.autocommit = True

    def save(self, item: StoredItem):
        keys = ','.join(item.get_value().keys())
        values = [f"'{str(x).replace('\'', '\"')}'" for x in item.get_value().values()]
        values = ','.join(values)
        self._conn.cursor().execute(f"""
            insert into {item.get_type()} ({keys})
            values ({values})
        """)
        

    def read(self, entity_type: str):
        return None