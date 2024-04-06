"""DataLad demo command"""

__docformat__ = 'restructuredtext'

import os.path
from os.path import curdir
from os.path import abspath

from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod
from datalad.interface.base import eval_results
from datalad.distribution.dataset import EnsureDataset
from datalad.support.constraints import EnsureNone, EnsureStr, EnsureChoice

from datalad.interface.results import get_status_dict

from datalad.distribution.dataset import require_dataset
from datalad.support.annexrepo import AnnexRepo

from dtoolcore.utils import sanitise_uri
from dtoolcore import DataSetCreator

import logging
lgr = logging.getLogger('datalad.dtool.export')


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class DtoolExport(Interface):
    """Export a dtool dataset as a snapshot of a datalad dataset

    Long description of arbitrary volume.
    """

    # parameters of the command, must be exhaustive
    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            doc="""Specify the dataset to export. If no dataset is given, an 
                   attempt is made to identify the dataset based on the current 
                   working directory. Constraints: Value must be a Dataset or a
                   valid identifier of a Dataset (e.g. a path) or value must be 
                   NONE.""",
            constraints=EnsureDataset() | EnsureNone()),
        target=Parameter(
            args=("base_uri",),
            nargs='?',
            metavar="BASE_URI",
            doc="""Target base URI where the  dtool dataset should be created 
                   from specified datalad dataset. Creates dtool dataset in 
                   current working directory if not specified.""",
            constraints=EnsureStr() | EnsureNone()),
        name=Parameter(
            args=("-n", "--name"),
            metavar="NAME",
            doc="""Name of dtool dataset to be created. Creates dtool dataset 
                   of same name as datalad dataset if not specified.""",
            constraints=EnsureStr() | EnsureNone()),
        missing_content=Parameter(
            args=("--missing-content",),
            doc="""By default, any discovered file with missing content will
                result in an error and the export is aborted. Setting this to
                'continue' will issue warnings instead of failing on error. The
                value 'ignore' will only inform about problem at the 'debug' log
                level. The latter two can be helpful when generating a TAR archive
                from a dataset where some file content is not available
                locally.""",
            constraints=EnsureChoice("error", "continue", "ignore")),
    )

    @staticmethod
    # decorator binds the command to the Dataset class as a method
    @datasetmethod(name='export_dtool')
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(base_uri=None,
                 *,
                 name=None,
                 dataset=None,
                 missing_content='error'):
        # commands should be implemented as generators and should
        # report any results by yielding status dictionaries
        if base_uri is None:
            base_uri = abspath(curdir)

        sanitised_base_uri = sanitise_uri(base_uri)

        dataset = require_dataset(dataset, check_installed=True,
                                  purpose='export dtool dataset')

        repo = dataset.repo
        # committed_date = repo.get_commit_date()

        datald_dataset_root_path = dataset.path
        lgr.debug("Export datalad dataset at '%s'", datald_dataset_root_path)
        if name is None:
            name = os.path.split(datald_dataset_root_path)[-1]

        lgr.debug("Export to dtool dataset of name '%s' at base URI '%s'",
                  (name, sanitised_base_uri))

        with DataSetCreator(name=name, base_uri=sanitised_base_uri) as dtool_dataset_creator:
            repo_files = repo.get_content_info(ref='HEAD', untracked='no')
            if isinstance(repo, AnnexRepo):
                # add availability (has_content) info
                repo_files = repo.get_content_annexinfo(ref='HEAD',
                                                        init=repo_files,
                                                        eval_availability=True)

            uri = dtool_dataset_creator.proto_dataset.uri
            lgr.debug("Created dataset will be available at '%s'", uri)

            for p, props in repo_files.items():
                if 'key' in props and not props.get('has_content', False):
                    if missing_content in ('ignore', 'continue'):
                        (lgr.warning if missing_content == 'continue' else lgr.debug)(
                            'File %s has no content available, skipped', p)
                        continue
                    else:
                        raise IOError('File %s has no content available' % p)
                # repath in the dtool dataset
                relpath = p.relative_to(repo.pathobj)
                fpath = dtool_dataset_creator.prepare_staging_abspath_promise(handle)
                # with open(fpath, "w") as fh:
                handle = dtool_dataset_creator.put_item(fpath, relpath)

                msg = f"Added item {handle}: {relpath} to dataset"
                yield get_status_dict(
                    # an action label must be defined, the command name make a good
                    # default
                    action='export-dtool',
                    # most results will be about something associated with a dataset
                    # (component), reported paths MUST be absolute
                    path=abspath(curdir),
                    # status labels are used to identify how a result will be reported
                    # and can be used for filtering
                    status='ok',
                    # arbitrary result message, can be a str or tuple. in the latter
                    # case string expansion with arguments is delayed until the
                    # message actually needs to be rendered (analog to exception
                    # messages)
                    message=msg)

        yield get_status_dict(
            # an action label must be defined, the command name make a good
            # default
            action='export-dtool',
            # most results will be about something associated with a dataset
            # (component), reported paths MUST be absolute
            path=abspath(curdir),
            # status labels are used to identify how a result will be reported
            # and can be used for filtering
            status='ok',
            # arbitrary result message, can be a str or tuple. in the latter
            # case string expansion with arguments is delayed until the
            # message actually needs to be rendered (analog to exception
            # messages)
            message=f"Created and froze dtool dataset {uri}.")