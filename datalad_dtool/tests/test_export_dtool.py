"""Test dtool dataset exporter"""

from datalad.tests.utils_pytest import assert_result_count

import os
import tarfile
import time
from os.path import isabs
from os.path import join as opj

from datalad.api import Dataset

from datalad.tests.utils_pytest import (
    assert_equal,
    assert_false,
    assert_not_equal,
    assert_raises,
    assert_result_count,
    assert_status,
    assert_true,
    ok_startswith,
    with_tree,
)
from datalad.utils import (
    chpwd,
    md5sum,
)

_dataset_template = {
    'ds': {
        'file_up': 'some_content',
        'dir': {
            'file1_down': 'one',
            'file2_down': 'two'}}}


def test_export_dtool_api():
    import datalad.api as da
    assert hasattr(da, 'export_dtool')


@with_tree(_dataset_template)
def test_failure(path=None):
    # non-existing dataset
    import datalad.api as da
    with assert_raises(ValueError):
        da.export_dtool(dataset=Dataset('nowhere'))


@with_tree(_dataset_template)
def test_archive(path=None):
    ds = Dataset(opj(path, 'ds')).create(force=True)
    ds.save()
    committed_date = ds.repo.get_commit_date()
    with chpwd(path):
        res = list(ds.export_dtool(base_uri=path, name=ds.id))
        assert_status('ok', res)
        assert_result_count(res, 1)
        assert(isabs(res[0]['path']))

    # TODO: replace with dtoolcore methods for inspecting content
    # def check_contents(outname, prefix):
    #     with tarfile.open(outname) as tf:
    #         nfiles = 0
    #         for ti in tf:
    #             # any annex links resolved
    #             assert_false(ti.issym())
    #             ok_startswith(ti.name, prefix + '/')
    #             assert_equal(ti.mtime, committed_date)
    #             if '.datalad' not in ti.name:
    #                 # ignore any files in .datalad for this test to not be
    #                 # susceptible to changes in how much we generate a meta info
    #                 nfiles += 1
    #         # we have exactly four files (includes .gitattributes for default
    #         # MD5E backend), and expect no content for any directory
    #         assert_equal(nfiles, 4)
    #
    # check_contents(default_outname, 'datalad_%s' % ds.id)
    # check_contents(custom_outname, 'myexport')

    # now loose some content
    ds.drop('file_up', reckless='kill')
    assert_raises(IOError, ds.export_dtool, base_uri=path, name='my')
    ds.export_dtool(base_uri=path, name='partial', missing_content='ignore')
    assert_true(os.path.exists(opj(path, 'partial')))