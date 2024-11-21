"""DataLad extension for the Climate Data Store"""

__docformat__ = "restructuredtext"
import logging

from typing import Literal

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
# import datalad_cds.spec
from dtoolcore.utils import sanitise_uri

logger = logging.getLogger("datalad.dtool.import")


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class DtoolImport(Interface):
    """Downloads specified datasets from the CDS data store"""

    _params_ = dict(
        dataset=Parameter(
            doc="""Specify the dataset to import. 
                   Constraints: Value must be a Dataset or a
                   valid identifier of a Dataset (e.g. a path) or value must be 
                   NONE.""",
        ),
        base_uri=Parameter(
            args=("-uri", "--base_uri"),
            metavar="PATH",
            doc="""specify the dataset to add files to. If no dataset is given,
            an attempt is made to identify the dataset based on the current
            working directory. Use [CMD: --nosave CMD][PY: save=False PY] to
            prevent adding files to the dataset.""",
        ),
        name=Parameter(
            args=("-n", "--name"),
            doc="""Name of datalad_dataset.""",
        ),
        missing_content=Parameter(
            args=("--missing-content",),
            doc="""By default, any discovered file with missing content will
                   result in an error and the export is aborted. Setting this to
                   'continue' will issue warnings instead of failing on error.
                   The value 'ignore' will only inform about problem at the
                   'debug' log level. The latter two can be helpful when
                   generating a TAR archive from a dataset where some file
                   content is not available locally.""",
            constraints=EnsureChoice("error", "continue", "ignore")),
    )

    @staticmethod
    @datasetmethod(name="import_dtool")
    @eval_results
    def __call__(
        base_uri:None,
        *,
        missing_content='error',
        name=None):
        if base_uri is None:
            base_uri = abspath(curdir)
        sanitised_base_uri = sanitise_uri(base_uri)
        yield get_status_dict(action="import-dtool", status="ok")


def ensure_special_remote_exists_and_is_enabled(
    repo: AnnexRepo, remote: Literal["dtool_remote"]
) -> None:
    """Initialize and enable the dtool special remote, if it isn't already.

    Very similar to datalad.customremotes.base.ensure_datalad_remote.
    """

    uuids = {"dtool": datalad_dtool.dtool_remote.DTOOL_REMOTE_UUID}
    uuid = uuids[remote]

    name = repo.get_special_remotes().get(uuid, {}).get("name")
    if not name:
        repo.init_remote(
            remote,
            [
                "encryption=none",
                "type=external",
                "autoenable=true",
                "externaltype={}".format(remote),
                "uuid={}".format(uuid),
            ],
        )
    elif repo.is_special_annex_remote(name, check_if_known=False):
        logger.debug("special remote %s is enabled", name)
    else:
        logger.debug("special remote %s found, enabling", name)
        repo.enable_remote(name)
