from datalad.tests.utils_pytest import assert_result_count


def test_export_dtool():
    import datalad.api as da
    assert hasattr(da, 'export_dtool')
