import logging
import shutil

from annexremote import Master
from annexremote import SpecialRemote
from annexremote import RemoteError

from dtoolcore import DataSet

logger = logging.getLogger(__name__)


class DtoolRemote(SpecialRemote):
    """A read-only special remote for retrieving files from dtool datasets."""
    transfer_store = None
    remove = None

    def __init__(self, annex):
        super().__init__(annex)
        self.configs = {
            'uri': "dtool dataset URI"
        }

    def initremote(self) -> None:
        # initialize the remote, e.g. create the folders
        # raise RemoteError if the remote couldn't be initialized
        self.uri = self.annex.getconfig("uri")
        if not self.uri:
            raise RemoteError("You need to set uri=")
        logger.debug("Set dtool dataset uri=%s", self.uri)

    def prepare(self) -> None:
        # prepare to be used, eg. open TCP connection, authenticate with the server etc.
        # raise RemoteError if not ready to use
        self.uri = self.annex.getconfig("uri")
        self.dtool_dataset = DataSet.from_uri(self.uri)

    def transfer_retrieve(self, key, filename):
        # get the file identified by `key` and store it to `filename`
        # raise RemoteError if the file couldn't be retrieved
        try:
            fpath = self.dtool_dataset.item_content_abspath(key)
        except Exception as e:
            raise RemoteError(e)
        shutil.copyfile(fpath, filename)

    def checkpresent(self, key):
        # return True if the key is present in the remote
        # return False if the key is not present
        # raise RemoteError if the presence of the key couldn't be determined, eg. in case of connection error
        if key in self.dtool_dataset.identifiers:
            return True
        else:
            return False

    def claimurl(self, url: str) -> bool:
        return url.startswith("dtool:")

    def checkurl(self, url: str) -> bool:
        return url.startswith("dtool:")

    def getcost(self) -> int:
        # This is a very expensive remote
        return 1000

    def getavailability(self) -> str:
        return "global"


def main() -> None:
     master = Master()
     remote = DtoolRemote(master)
     master.LinkRemote(remote)
     master.Listen()