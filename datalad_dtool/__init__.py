"""DataLad demo extension"""

__docformat__ = 'restructuredtext'

import logging
lgr = logging.getLogger('datalad.dtool')

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "DataLad-dtool command suite",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            'datalad_dtool.export',
            # name of the command class implementation in above module
            'DtoolExport',
            # optional name of the command in the cmdline API
            'export-dtool',
            # optional name of the command in the Python API
            'export_dtool'
        ),
        (
            'datalad_dtool.import',
            'DtoolImport',
            'import-dtool',
            'import_dtool'
        ),
    ]
)

from . import _version
__version__ = _version.get_versions()['version']
