from .license import update_copyright_year


def test_no_copyright():
    input = """
    Does not contain a copyright year
    """
    expected = input
    actual = update_copyright_year(input, 2021)
    assert expected == actual


def test_same_year_copyright():
    input = """
Copyright (c) 2021 Nikolaos Georgiou
    """
    expected = input
    actual = update_copyright_year(input, 2021)
    assert expected == actual


def test_same_year_range_copyright():
    input = """
Copyright (c) 2020-2021 Nikolaos Georgiou
    """
    expected = input
    actual = update_copyright_year(input, 2021)
    assert expected == actual


def test_old_year_single_year_copyright():
    input = """
Copyright (c) 2020 Nikolaos Georgiou
    """
    expected = """
Copyright (c) 2020-2021 Nikolaos Georgiou
    """
    actual = update_copyright_year(input, 2021)
    assert expected == actual


def test_old_year_year_range_copyright():
    input = """
Copyright (c) 2019-2020 Nikolaos Georgiou
    """
    expected = """
Copyright (c) 2019-2021 Nikolaos Georgiou
    """
    actual = update_copyright_year(input, 2021)
    assert expected == actual
