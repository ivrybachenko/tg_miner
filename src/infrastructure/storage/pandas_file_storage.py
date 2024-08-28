from abc import ABC, abstractmethod

import pandas as pd
import os
from enum import Enum
from .storage import Storage, StoredItem

class ON_CONFLICT_MODE(Enum):
    """
    How storage should act when inserting entity with duplicated key. 
    """

    # Keep old row, insert new row.
    INSERT = 0,
    # Remove old row, insert new row.
    UPDATE = 1,
    # Keep old row, remove new row.
    SKIP = 2

class PandasFileStorage(Storage, ABC):
    """
    Stores result into CSV files.
    """
    _out_dir = None
    _on_conflict = None
    _total_count = {}

    def __init__(self, out_dir: str, on_conflict: ON_CONFLICT_MODE = ON_CONFLICT_MODE.INSERT):
        """
        Constructor.

        Parameters
        ----------
        out_dir: str
            Directory where CSV files will be stored.
        """
        self._out_dir = out_dir
        self._on_conflict = on_conflict
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if len(os.listdir(out_dir)) > 0:
            raise Exception('Output directory is not empty. " + \
                "Can save results only into the empty directory.')

    def save(self, item: StoredItem):
        filename = self._get_filename(item.get_type())
        total_count = self._total_count.get(filename, 0)
        try:
            df = self._read_file(filename)
        except:
            df = pd.DataFrame(columns=list(item.get_value().keys()))
        if self._on_conflict == ON_CONFLICT_MODE.UPDATE:
            if df[df[item.get_key()] == item.get_value()[item.get_key()]].shape[0] > 0:
                # update existing row
                df.loc[df[item.get_key()] == item.get_value()[item.get_key()], :] = item.get_value().values()
            else:
                # insert new row
                df.loc[total_count] = item.get_value()
        elif self._on_conflict == ON_CONFLICT_MODE.INSERT:
            df.loc[total_count] = item.get_value()
        elif self._on_conflict == ON_CONFLICT_MODE.SKIP:
            if df[df[item.get_key()] == item.get_value()[item.get_key()]].shape[0] > 0:
                # on conflict do not save new row
                pass
            else:
                # insert new row
                df.loc[total_count] = item.get_value()
        self._write_file(filename, df)
        self._total_count[filename] = total_count + 1

    @abstractmethod
    def _read_file(self, filename) -> pd.DataFrame:
        pass

    @abstractmethod
    def _write_file(self, filename, df: pd.DataFrame):
        pass