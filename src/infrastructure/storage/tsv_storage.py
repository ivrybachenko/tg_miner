import os
from .storage import StoredItem, Storage


class TsvStorage(Storage):
    """
    Stores result into TSV files.
    """
    _out_dir = None
    _total_count = {}

    def __init__(self, out_dir: str):
        """
        Constructor.

        Parameters
        ----------
        out_dir: str
            Directory where TSV files will be stored.
        """
        self._out_dir = out_dir
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        # if len(os.listdir(out_dir)) > 0:
        #     raise Exception(f'Output directory is not empty [{out_dir}]. " + \
        #         "Can save results only into the empty directory.')
    
    def save(self, item: StoredItem):
        filename = self._get_filename(item.get_type())
        if not os.path.exists(filename):
            with open(filename, 'a') as f:
                header = '\t'.join([str(x) for x in item.get_value().keys()])
                f.write(header)
                f.write('\r\n')
        with open(filename, 'a') as f:
                row = '\t'.join([str(x).replace('\n', r'\n') for x in item.get_value().values()])
                f.write(row)
                f.write('\r\n')

    def _get_filename(self, entity_type: str):
        return os.path.join(self._out_dir, entity_type) + '.tsv'

    def read(self, entity_type: str):
        filename = self._get_filename(entity_type)
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            return f.read()