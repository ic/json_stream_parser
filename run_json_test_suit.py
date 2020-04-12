import os
import traceback
import glob
import json
from json_stream_parser import load_iter, JSONDecodeError


def not_pass(case):
    print('NOT_PASS', case)


def y(case):
    with open(case, 'rt', encoding='utf-8') as fp:
        expected = json.dumps(json.load(fp))
    with open(case, 'rt', encoding='utf-8') as fp:
        try:
            got = '\n'.join(json.dumps(obj) for obj in load_iter(fp))
        except JSONDecodeError as exc:
            not_pass(case)
            traceback.print_exc()
            return

    if expected != got:
        not_pass(case)
        print('expect', expected, 'got', got)


def n(case):
    with open(case, 'rt', encoding='utf-8') as fp:
        good = 0
        try:
            for obj in load_iter(fp):
                good += 1
        except JSONDecodeError:
            return
        except UnicodeDecodeError:
            return
        except RecursionError:
            return

        if good == 1:
            not_pass(case)


def i(case):
    ok = True
    with open(case, 'rt', encoding='utf-8') as fp:
        try:
            json.load(fp)
        except json.JSONDecodeError:
            ok = False
        except UnicodeDecodeError:
            ok = False

    if ok:
        y(case)
    else:
        n(case)


def main():
    # https://github.com/nst/JSONTestSuite
    dir_path = os.path.join(os.path.dirname(__file__), '../JSONTestSuite/test_parsing')
    dir_path = os.path.normpath(dir_path)

    for case in glob.glob(os.path.join(dir_path, 'y_*.json')):
        y(case)
    for case in glob.glob(os.path.join(dir_path, 'n_*.json')):
        n(case)
    for case in glob.glob(os.path.join(dir_path, 'i_*.json')):
        i(case)


if __name__ == '__main__':
    main()
