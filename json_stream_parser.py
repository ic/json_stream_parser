from typing import Tuple, Union, List, Dict


__all__ = ('load_iter', 'JSONDecodeError')


class JSONDecodeError(Exception):
    def __init__(self, msg, *args):
        super().__init__(msg % args)


class JSONEOFError(JSONDecodeError):
    pass


# TODO: options
def load_iter(fp, *, object_pairs_hook=dict):
    ch = ''
    while True:
        try:
            ch = _skip_ch_space(ch, fp)
        except JSONEOFError:
            return
        obj, ch = _load_obj(ch, fp, object_pairs_hook=object_pairs_hook)
        yield obj


Value = Union[int, float, str, None, List['Value'], Dict[str, 'Value']]


def _load_obj(ch, fp, *, object_pairs_hook) -> Tuple[Value, str]:
    if ch == '{':
        ch = ''
        pairs = []
        while True:
            ch = _skip_ch_space(ch, fp)
            if ch == '}':
                return object_pairs_hook(pairs), ''

            if pairs:
                if ch != ',':
                    raise JSONDecodeError('expect comma, got %r', ch)
                ch = _skip_space(fp)

            if ch != '"':
                raise JSONDecodeError('expect quote, got %r', ch)
            key = _load_str(fp)

            ch = _skip_space(fp)
            if ch != ':':
                raise JSONDecodeError('expect colon, got %r', ch)

            val, ch = _load_obj(_skip_space(fp), fp, object_pairs_hook=object_pairs_hook)

            pairs.append((key, val))
    elif ch == '[':
        ch = ''
        rv = []
        while True:
            ch = _skip_ch_space(ch, fp)
            if ch == ']':
                return rv, ''

            if len(rv) > 0:
                if ch != ',':
                    raise JSONDecodeError('expect comma, got %r', ch)
                ch = _skip_space(fp)

            val, ch = _load_obj(ch, fp, object_pairs_hook=object_pairs_hook)
            rv.append(val)
    elif ch == 't':
        _expect(fp, 'rue')
        return True, ''
    elif ch == 'f':
        _expect(fp, 'alse')
        return False, ''
    elif ch == 'n':
        _expect(fp, 'ull')
        return None, ''
    elif ch == '"':
        return _load_str(fp), ''
    elif ch in '0123456789-':
        return _load_num(ch, fp)
    else:
        raise JSONDecodeError('unknown char: %r', ch)


def _expect(fp, tok):
    if tok != fp.read(len(tok)):
        raise JSONDecodeError('expect %r', tok)


_ESC_MAP = {
    '"': '"',
    "\\": '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}


def _load_str(fp) -> str:
    rv = []
    while True:
        ch = _read_char(fp, 'got eof on string')
        if ch == '"':
            return ''.join(rv)
        elif ch == '\\':
            ch = _read_char(fp, 'got eof on string escape')
            if ch in _ESC_MAP:
                rv.append(_ESC_MAP[ch])
            elif ch == 'u':
                digits = fp.read(4)
                if len(digits) != 4:
                    raise JSONDecodeError('expect 4-hex-digits')
                try:
                    ch = chr(int(digits, 16))
                except ValueError:
                    raise JSONDecodeError('expect 4-hex-digits: got %r', digits)
                rv.append(ch)
            else:
                raise JSONDecodeError('bad excape')
        else:
            if ord(ch) <= 0x1f:
                raise JSONDecodeError('unexpected control char: %r', ch)
            rv.append(ch)


def _read_char(fp, errmsg) -> str:
    ch = fp.read(1)
    if not ch:
        raise JSONDecodeError(errmsg)
    return ch


def _load_num(ch: str, fp) -> Tuple[Union[int, float], str]:
    s = ch

    # sign
    if ch == '-':
        ch = _read_char(fp, 'expect number')
        s += ch

    # first digits of int
    if ch not in '0123456789':
        raise JSONDecodeError('expected 0123456789, got: %r', ch)
    is_zero = (ch == '0')

    # remain of int
    digits, ch = _maybe_digits(fp)  # NOTE: ch may be ''
    s += digits

    # check leading zero
    if is_zero and digits:
        raise JSONDecodeError('digits follows zero')

    # frac
    is_float = False
    if ch == '.':
        is_float = True
        digits, ch = _expect_digits(fp)
        s += '.' + digits

    # exp
    if ch and ch in 'eE':
        is_float = True
        s += ch
        ch = _read_char(fp, 'expect exp')
        if ch in '+-':
            s += ch
            ch = _read_char(fp, 'expect exp digits')

        if ch not in '0123456789':
            raise JSONDecodeError('expected 0123456789, got: %r', ch)
        s += ch

        digits, ch = _maybe_digits(fp)
        s += digits

    if is_float:
        return float(s), ch
    else:
        return int(s), ch


def _expect_digits(fp):
    ch = _read_char(fp, 'expect digits')
    if ch not in '0123456789':
        raise JSONDecodeError('expected 0123456789, got: %r', ch)

    digits, next_ch = _maybe_digits(fp)
    return ch + digits, next_ch


def _maybe_digits(fp) -> Tuple[str, str]:
    s = ''
    while True:
        ch = fp.read(1)
        if ch and ch in '0123456789':
            s += ch
        else:
            break

    return s, ch


def _skip_space(fp) -> str:
    while True:
        ch = fp.read(1)
        if not ch:
            raise JSONEOFError('unexpected EOF')

        if ch not in ' \t\n\r':
            return ch


def _skip_ch_space(ch, fp) -> str:
    if ch and ch not in ' \t\n\r':
        return ch
    return _skip_space(fp)


def main():
    import sys
    import json
    for obj in load_iter(sys.stdin):
        print(json.dumps(obj, ensure_ascii=False), end='\n')


if __name__ == '__main__':
    main()
