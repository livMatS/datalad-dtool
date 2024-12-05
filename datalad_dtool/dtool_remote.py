import logging
import shutil

from annexremote import Master
from annexremote import ExportRemote
from annexremote import RemoteError

from dtoolcore import DataSet, ProtoDataSet, DtoolCoreTypeError


logger = logging.getLogger(__name__)


def extract_backend(key):
    # Split the key by "--"
    parts = key.split("-")

    if len(parts) < 2:
        return None  # Invalid key format

    # Get the last part (hash + possible extension)
    return parts[0]


    return hash_only


def extract_hash(key):
    # Split the key by "--"
    parts = key.split("--")

    if len(parts) < 2:
        return None  # Invalid key format

    # Get the last part (hash + possible extension)
    hash_part = parts[-1]

    # Remove file extension if present
    hash_only = hash_part.split('.')[0]

    return hash_only


class DtoolRemote(ExportRemote):
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
        try:
            self.dtool_dataset = DataSet.from_uri(self.uri)
            logger.debug("Dataset uri=%s frozen, immutable.", self.uri)
        except DtoolCoreTypeError as exc:
            logger.warning(exc)
            self.dtool_dataset = ProtoDataSet.from_uri(self.uri)
        pass

    def transfer_retrieve(self, key, filename):
        # get the file identified by `key` and store it to `filename`
        # raise RemoteError if the file couldn't be retrieved
        exceptions = []

        backend = self.annex.getconfig('keybackend_' + key)
        logger.debug("Key %s uses backend %s", key, backend)

        file_hash = extract_backend(key)

        logger.debug("Try to locate file of chekcsum/hash %s in dataset %s", file_hash, self.uri)
        manifest = self.dtool_dataset.generate_manifest()
        if backend.startswith('MD5') and (manifest["hash_function"] == "md5sum_hexdigest"):
            for uuid, entry in manifest['items'].items():
                if entry["hash"] == file_hash:
                    try:
                        fpath = self.dtool_dataset.item_content_abspath(uuid)
                        shutil.copyfile(fpath, filename)
                        return
                    except Exception as e:
                        exceptions.append(e)

        urls = self.annex.geturls(key, f"dtool:{self.uri}")
        logger.debug("Retrieve from %s", urls)

        for url in urls:
            url = url[len('dtool:'):]
            try:
                dataset_uri, item_uuid = url.rsplit('/', 1)

                assert dataset_uri == self.uri

                logger.debug("Try to retrieve item %s from dataset %s", item_uuid, dataset_uri)
                # dtool_dataset = DataSet.from_uri(dataset_uri)
                fpath = self.dtool_dataset.item_content_abspath(item_uuid)
                logger.debug("Cached item content at %s", fpath)
                shutil.copyfile(fpath, filename)
                return
            except Exception as e:
                exceptions.append(e)

        raise RemoteError(exceptions)

    def checkpresent(self, key):
        # return True if the key is present in the remote
        # return False if the key is not present
        # raise RemoteError if the presence of the key couldn't be determined, eg. in case of connection error

        # first, try to identify file from actual md5 key

        exceptions = []

        backend = extract_backend(key)
        logger.debug("Key %s uses backend %s", key, backend)

        try:
            file_hash = extract_hash(key)
            logger.debug("Try to locate hash/checksum %s in dataset %s", file_hash, self.uri)

            manifest = self.dtool_dataset.generate_manifest()
            if backend.startswith('MD5') and (manifest["hash_function"] == "md5sum_hexdigest"):
                for uuid, entry in manifest['items'].items():
                    if entry["hash"] == file_hash:
                        logger.debug("Located item %s in dataset %s", uuid, self.uri)
                        return True
        except Exception as e:
            exceptions.append(e)

        # next, try to identify file from dtool URLs

        urls = self.annex.geturls(key, f"dtool:{self.uri}")

        for url in urls:
            url = url[len('dtool:'):]
            try:
                dataset_uri, item_uuid = url.rsplit('/', 1)

                assert dataset_uri == self.uri

                logger.debug("Try to locate item %s in dataset %s", item_uuid, dataset_uri)

                # dtool_dataset = DataSet.from_uri(dataset_uri)
                manifest = self.dtool_dataset.generate_manifest()
                if item_uuid in manifest['items']:
                    logger.debug("Located item %s in dataset %s", item_uuid, dataset_uri)
                    return True

            except Exception as e:
                exceptions.append(e)

        if len(exceptions) > 0:
            raise exceptions[-1]
        
        return False

    def claimurl(self, url: str) -> bool:
        logger.debug("Check claim to URL %s", url)
        return url.startswith(f"dtool:{self.uri}/")

    def checkurl(self, url: str) -> bool:
        return url.startswith(f"dtool:{self.uri}/")
        # TODO: implement more sophisticated checking on URL

    def getcost(self) -> int:
        # This is a very expensive remote
        return 1000

    def getavailability(self) -> str:
        return "global"

    ## Export methods
    def transferexport_store(self, key, local_file, remote_file):
        pass

    def transferexport_retrieve(self, key, local_file, remote_file):
        manifest = self.dtool_dataset.generate_manifest()
        for uuid, entry in manifest['items'].items():
            if entry["relpath"] == remote_file:
                try:
                    fpath = self.dtool_dataset.item_content_abspath(uuid)
                    shutil.copyfile(fpath, local_file)
                except Exception as e:
                    raise RemoteError(e)

        pass

    def checkpresentexport(self, key, remote_file):
        pass

    def removeexport(self, key, remote_file):
        pass

    def removeexportdirectory(self, remote_directory):
        pass


def main() -> None:
     master = Master()
     remote = DtoolRemote(master)
     master.LinkRemote(remote)
     master.Listen()