#!/usr/bin/env python
from __future__ import division, print_function

import sys
import json

from logstash_filter_run import logstash_filter_run


# This is copied from https://github.com/linjackson78/jstyleson
# The MIT License (MIT) Copyright (c) 2016 linjackson
def dispose(json_str):
    """Clear all comments in json_str.
    Clear JS-style comments like // and /**/ in json_str.
    Accept a str or unicode as input.
    Args:
        json_str: A json string of str or unicode to clean up comment
    Returns:
        str: The str without comments (or unicode if you pass in unicode)
    """
    result_str = list(json_str)
    escaped = False
    normal = True
    sl_comment = False
    ml_comment = False
    quoted = False

    a_step_from_comment = False
    a_step_from_comment_away = False

    former_index = None

    for index, char in enumerate(json_str):

        if escaped:  # We have just met a '\'
            escaped = False
            continue

        if a_step_from_comment:  # We have just met a '/'
            if char != '/' and char != '*':
                a_step_from_comment = False
                normal = True
                continue

        if char == '"':
            if normal and not escaped:
                # We are now in a string
                quoted = True
                normal = False
            elif quoted and not escaped:
                # We are now out of a string
                quoted = False
                normal = True

        elif char == '\\':
            # '\' should not take effect in comment
            if normal or quoted:
                escaped = True

        elif char == '/':
            if a_step_from_comment:
                # Now we are in single line comment
                a_step_from_comment = False
                sl_comment = True
                normal = False
                former_index = index - 1
            elif a_step_from_comment_away:
                # Now we are out of comment
                a_step_from_comment_away = False
                normal = True
                ml_comment = False
                for i in range(former_index, index + 1):
                    result_str[i] = ""

            elif normal:
                # Now we are just one step away from comment
                a_step_from_comment = True
                normal = False

        elif char == '*':
            if a_step_from_comment:
                # We are now in multi-line comment
                a_step_from_comment = False
                ml_comment = True
                normal = False
                former_index = index - 1
            elif ml_comment:
                a_step_from_comment_away = True
        elif char == '\n':
            if sl_comment:
                sl_comment = False
                normal = True
                for i in range(former_index, index + 1):
                    result_str[i] = ""
        elif char == ']' or char == '}':
            if normal:
                _remove_last_comma(result_str, index)

    # Show respect to original input if we are in python2
    return ("" if isinstance(json_str, str) else u"").join(result_str)


# There may be performance suffer backtracking the last comma
def _remove_last_comma(str_list, before_index):
    i = before_index - 1
    while str_list[i].isspace() or not str_list[i]:
        i -= 1

    # This is the first none space char before before_index
    if str_list[i] == ',':
        str_list[i] = ''


def print_results(testcases, outputs):
    expecteds = [expected for _inp, expected in testcases]
    n_errs = 0

    def json_dumps(x):
        return json.dumps(x, indent=2, sort_keys=True)
    for i, (expected, output) in enumerate(zip(expecteds, outputs)):
        if not all(output.get(k) == v for k, v in expected.items()):
            print("Testcase {} failed:".format(i))
            for k, v in sorted(expected.items()):
                v2 = output.get(k)
                if v != v2:
                    print("  {}:".format(k))
                    print("    output:   {}".format(json_dumps(v2)))
                    print("    expected: {}".format(json_dumps(v)))
            print("Full output document:")
            print(json_dumps(output))
            print("=================================")
            print()
            n_errs += 1
    if n_errs == 0:
        print("All {} tests successful.".format(len(testcases)))
    else:
        print("{} / {} tests failed.".format(n_errs, len(testcases)))
    return n_errs


def logstash_filter_test(filter_fn='filter.conf', testcases_fn='testcases.js'):
    testcases = json.loads(dispose(open(testcases_fn).read()))
    inputs = [inp for inp, _expected in testcases]
    filter_def = open(filter_fn).read()
    outputs = logstash_filter_run(inputs, filter_def)
    n_errs = print_results(testcases, outputs)
    return outputs, n_errs


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Test logstash filters")
    parser.add_argument("--filters", default="filter.conf",
                        help="File with logstash filter definition to test. default: filter.conf")
    parser.add_argument("--testcases", default="testcases.js",
                        help="File with testcases. default: testcases.js")
    args = parser.parse_args()

    _outputs, n_errs = logstash_filter_test(args.filters, args.testcases)

    return 0 if n_errs == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
