import pandas as pd
import os
from .pandas_file_storage import PandasFileStorage


class TsvStorage(PandasFileStorage):

    def _get_filename(self, entity_type: str):
        return os.path.join(self._out_dir, entity_type) + '.tsv'

    def _read_file(self, filename) -> pd.DataFrame:
        return pd.read_csv(filename, sep='\t')

    def _write_file(self, filename, df: pd.DataFrame):
        return df.to_csv(filename, index=False, sep='\t')