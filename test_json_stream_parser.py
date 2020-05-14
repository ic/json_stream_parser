import json
import io
import pytest
from json_stream_parser import load_iter, JSONDecodeError


def test_ok_coverage():
    cases = r'''
        0
        -0
        0.1
        0e1
        123
        1.2
        1.123
        1.3e9
        1e9
        1e+1
        1E-1
        -1
        ""
        "asdf"
        "\u0020"
        "\b\f\n\r\t\\\/\""
        []
        [[]]
        [1]
        ["asdf", 123]
        {}
        {"": ""}
        {"1": 1, "2": 2}
        true
        false
        null
    '''

    expected = '\n'.join([json.dumps(json.loads(x)) for x in cases.splitlines() if x.strip()])
    parsed = '\n'.join(json.dumps(x) for x in load_iter(io.StringIO(cases)))
    assert expected == parsed


def test_bad_coverage():
    cases = r'''
        {"": 1 ""}
        {1: 2}
        {"1" 2}
        [1 2]
        haha
        "\u123
        "\ufffg"
        "\?"
        tru
        -.1
        00
        01
        1ee
        1.e
        -
    ''' + '"\x01"'
    for line in cases.splitlines():
        if line.strip():
            stream = load_iter(io.StringIO(line))
            with pytest.raises(JSONDecodeError):
                next(stream)


def test_splat_depth_1():
    data = json.dumps([ { 'test': 0 } ] * 3)
    expected = data[1:-1].replace(', ', '\n')
    parsed = '\n'.join(json.dumps(x) for x in load_iter(io.StringIO(data), splat_depth=1))
    assert expected == parsed


def test_splat_depth_2():
    data = json.dumps([[ { 'test': 0 } ] * 3])
    expected = data[2:-2].replace(', ', '\n')
    parsed = '\n'.join(json.dumps(x) for x in load_iter(io.StringIO(data), splat_depth=2))
    assert expected == parsed
