import pandas as pd
import os
from .storage import Storage, StoredItem


class CsvStorage(Storage):
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

    def save(self, item: StoredItem):
        filename = self._get_filename(item.get_type())
        try:
            df = pd.read_csv(filename)
        except:
            df = pd.DataFrame(columns=list(item.get_value().keys()))
        if df[df[item.get_key()] == item.get_value()[item.get_key()]].shape[0] > 0:
            # update existing row
            df.loc[df[item.get_key()] == item.get_value()[item.get_key()], :] = item.get_value().values()
        else:
            # insert new row
            num_rows = df.shape[0]
            df.loc[num_rows] = item.get_value()
        df.to_csv(filename, index=False)

    def _get_filename(self, entity_type: str):
        return os.path.join(self._out_dir, entity_type) + '.csv'