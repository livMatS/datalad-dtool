from datalad.tests.utils_pytest import assert_result_count


def test_dtool_export():
    import datalad.api as da
    assert hasattr(da, 'hello_cmd')
    assert_result_count(
        da.hello_cmd(),
        1,
        action='demo')

