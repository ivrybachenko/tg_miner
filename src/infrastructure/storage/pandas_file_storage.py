from abc import ABC, abstractmethod

import pandas as pd
import os
from .storage import Storage, StoredItem


class PandasFileStorage(Storage, ABC):
    """
    Stores result into CSV files.
    """
    _out_dir = None

    def __init__(self, out_dir: str):
        """
        Constructor.

        Parameters
        ----------
        out_dir: str
            Directory where CSV files will be stored.
        """
        self._out_dir = out_dir
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if len(os.listdir(out_dir)) > 0:
            raise Exception('Output directory is not empty. " + \
                "Can save results only into the empty directory.')

    def save(self, item: StoredItem):
        filename = self._get_filename(item.get_type())
        try:
            df = self._read_file(filename)
        except:
            df = pd.DataFrame(columns=list(item.get_value().keys()))
        if df[df[item.get_key()] == item.get_value()[item.get_key()]].shape[0] > 0:
            # update existing row
            df.loc[df[item.get_key()] == item.get_value()[item.get_key()], :] = item.get_value().values()
        else:
            # insert new row
            num_rows = df.shape[0]
            df.loc[num_rows] = item.get_value()
        self._write_file(filename, df)

    @abstractmethod
    def _read_file(self, filename) -> pd.DataFrame:
        pass

    @abstractmethod
    def _write_file(self, filename, df: pd.DataFrame):
        pass