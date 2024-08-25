import pandas as pd
import os
from src.storage import Storage
from src.telegram import Channel, Message

class CsvStorage(Storage):
    """
    Stores result into CSV files.
    """

    _messages_filename: str = None
    _channels_filename: str = None

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
        self._messages_filename = os.path.join(out_dir, 'messages.csv')
        self._channels_filename = os.path.join(out_dir, 'channels.csv')

    def save_channel(self, channel: Channel):
        try:
            df = pd.read_csv(self._channels_filename)
        except:
            df = pd.DataFrame(columns=['id', 'title'])
        num_rows = df.shape[0]
        df.loc[num_rows] = {'id': channel.id, 'title': channel.title}
        df.drop_duplicates().to_csv(self._channels_filename, index=False)

    def save_message(self, message: Message):
        try:
            df = pd.read_csv(self._messages_filename)
        except:
            df = pd.DataFrame(columns=['id', 'text'])
        num_rows = df.shape[0]
        df.loc[num_rows] = {'id': message.id, 'text': message.text}
        df.drop_duplicates().to_csv(self._messages_filename, index=False)