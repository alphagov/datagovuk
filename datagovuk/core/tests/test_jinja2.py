from datagovuk.core.jinja2 import combine


def test_combine_flat_dicts():
    dict_1 = {"foo": "bar"}
    dict_2 = {"baz": "woop"}
    result = combine(dict_1, dict_2)
    assert result == {"foo": "bar", "baz": "woop"}


def test_combine_flat_dict_and_deep_dict():
    dict_1 = {"foo": "bar"}
    dict_2 = {"baz": {"hello": "woop"}}
    result = combine(dict_1, dict_2)
    assert result == {"foo": "bar", "baz": {"hello": "woop"}}


def test_combine_deep_dicts():
    dict_1 = {"foo": {"1": "bar"}}
    dict_2 = {"foo": {"2": "baz"}}
    result = combine(dict_1, dict_2)
    assert result == {"foo": {"1": "bar", "2": "baz"}}


def test_combine_non_dict():
    dict_1 = {"foo": {"1": "bar"}}
    result = combine(dict_1, None)
    assert result == dict_1
