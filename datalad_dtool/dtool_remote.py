import logging
import shutil

from annexremote import Master
from annexremote import SpecialRemote
from annexremote import RemoteError

from dtoolcore import DataSet, ProtoDataSet, DtoolCoreTypeError

logger = logging.getLogger(__name__)


class DtoolRemote(SpecialRemote):
    """A read-only special remote for retrieving files from dtool datasets."""
    transfer_store = None
    remove = None

    def __init__(self, annex):
        super().__init__(annex)

    def initremote(self) -> None:
        # initialize the remote, e.g. create the folders
        # raise RemoteError if the remote couldn't be initialized
        pass

    def prepare(self) -> None:
        # prepare to be used, eg. open TCP connection, authenticate with the server etc.
        # raise RemoteError if not ready to use
        pass

    def transfer_retrieve(self, key, filename):
        # get the file identified by `key` and store it to `filename`
        # raise RemoteError if the file couldn't be retrieved
        urls = self.annex.geturls(key, "dtool:")
        logger.debug("Retrieve from %s", urls)

        exceptions = []
        for url in urls:
            url = url[len('dtool:'):]
            try:
                dataset_uri, item_uuid = url.rsplit('/', 1)
                logger.debug("Try to retrieve item %s from dataset %s", item_uuid, dataset_uri)
                dtool_dataset = DataSet.from_uri(dataset_uri)
                fpath = dtool_dataset.item_content_abspath(item_uuid)
                logger.debug("Cached item content at %s", fpath)
                shutil.copyfile(fpath, filename)
                break
            except Exception as e:
                exceptions.append(e)
        else:
            raise RemoteError(exceptions)

    def checkpresent(self, key):
        # return True if the key is present in the remote
        # return False if the key is not present
        # raise RemoteError if the presence of the key couldn't be determined, eg. in case of connection error
        logger.debug("Looking for item %s in dataset %s", key, self.uri)

        urls = self.annex.geturls(key, "dtool:")

        for url in urls:
            url = url[len('dtool:'):]
            try:
                dataset_uri, item_uuid = url.rsplit('/', 1)
                logger.debug("Try to locate item %s in dataset %s", item_uuid, dataset_uri)

                dtool_dataset = DataSet.from_uri(dataset_uri)
                manifest = dtool_dataset.generate_manifest()
                if item_uuid in manifest['items']:
                    logger.debug("Located item %s in dataset %s", item_uuid, dataset_uri)
                    return True

            except Exception as e:
                exceptions.append(e)

        return False

        logger.debug("Present at %s", urls)

        if isinstance(self.dtool_dataset, ProtoDataSet):
            self.dtool_dataset.freeze()
            self.dtool_dataset = DataSet.from_uri(self.uri)



        return False

    def claimurl(self, url: str) -> bool:
        return url.startswith("dtool:")

    def checkurl(self, url: str) -> bool:
        return url.startswith("dtool:")
        # TODO: implement more sophisticated checking on URL

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