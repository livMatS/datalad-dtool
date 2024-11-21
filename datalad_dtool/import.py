"""DataLad extension for the Climate Data Store"""

__docformat__ = "restructuredtext"
import logging

from typing import Literal, Optional

from datalad.distribution.dataset import (
    EnsureDataset,
    datasetmethod,
    require_dataset,
)
from datalad.interface.base import Interface, build_doc, eval_results
from datalad.interface.common_opts import nosave_opt, save_message_opt
from datalad.interface.results import get_status_dict
from datalad.support.annexrepo import AnnexRepo
from datalad.support.constraints import EnsureNone, EnsureStr, EnsureChoice
from datalad.support.param import Parameter

import datalad_dtool.dtool_remote

from dtoolcore import DataSet
from dtoolcore.utils import sanitise_uri

logger = logging.getLogger("datalad.dtool.import")


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class DtoolImport(Interface):
    """Import a dtool dataset into a datalad dataset"""

    _params_ = dict(
        uri=Parameter(
            args=("uri",),
            metavar="URI",
            doc="""dtool URI of dtool dataset to import.""",
            constraints=EnsureStr() | EnsureNone()),
        dataset=Parameter(
            args=("-d", "--dataset"),
            doc="""specify the datalad dataset to add files to. If no 
                   datalad dataset is given, an attempt is made to identify the dataset 
                   based on the current working directory. Use 
                   [CMD: --nosave CMD][PY: save=False PY] to
                   prevent adding files to the dataset.""",
            constraints=EnsureDataset() | EnsureNone()),
        path=Parameter(
            args=("-O", "--path"),
            doc="""Relative target path to import to within datalad dataset.""",
            constraints=EnsureStr() | EnsureNone(),
        ),
        save=nosave_opt,
        message=save_message_opt,
    )

    @staticmethod
    @datasetmethod(name="import_dtool")
    @eval_results
    def __call__(
        uri: str,
        *,
        dataset: Optional[str] = None,
        path: Optional[str] = None,
        message: Optional[str] = None,
        save: bool = True):
        # if uri is None:
        #    uri = abspath(curdir)
        sanitised_uri = sanitise_uri(uri)
        logger.debug("Sanitized dtool dataset URI: %s", sanitised_uri)


        ds = require_dataset(dataset, check_installed=True)
        ensure_special_remote_exists_and_is_enabled(
            repo=ds.repo, remote="dtool", uri=sanitised_uri)

        if path is None:
            pathobj = ds.pathobj
        else:
            pathobj = ds.pathobj / path

        dtool_dataset = DataSet.from_uri(sanitised_uri)
        manifest = dtool_dataset.generate_manifest()
        for uuid, entry in manifest['items'].items():
            relpath = entry["relpath"]
            file_pathobj = pathobj / relpath
            dtool_item_uri = f'dtool:{uri}/{uuid}'
            logger.debug(
                "Import dtool dataset URI '%s' item '%s' to path '%s' within '%s'",
                sanitised_uri, uuid, relpath, pathobj)
            ds.repo.add_url_to_file(file_pathobj, dtool_item_uri)

        if save:
            msg = (
                message
                if message is not None
                else "[DATALAD] import from dtool dataset '{}'".format(uri)
            )
            yield ds.save(pathobj, message=msg)

        yield get_status_dict(action="import-dtool", ds=ds, status="ok")


def ensure_special_remote_exists_and_is_enabled(
    repo: AnnexRepo, remote: Literal["dtool"], uri: str,
) -> None:
    """Initialize and enable the dtool special remote, if it isn't already.

    Very similar to datalad.customremotes.base.ensure_datalad_remote.
    """

    uuids = {"dtool": datalad_dtool.dtool_remote.DTOOL_REMOTE_UUID}
    uuid = uuids[remote]

    name = repo.get_special_remotes().get(uuid, {}).get("name")
    if not name:
        logger.debug("no suitable special remote found, initialize dtool remote")
        repo.init_remote(
            remote,
            [
                "encryption=none",
                "type=external",
                "autoenable=true",
                "externaltype={}".format(remote),
                "uuid={}".format(uuid),
                "uri={}".format(uri)
            ],
        )
    elif repo.is_special_annex_remote(name, check_if_known=False):
        logger.debug("special remote %s is enabled", name)
    else:
        logger.debug("special remote %s found, enabling", name)
        repo.enable_remote(name)
