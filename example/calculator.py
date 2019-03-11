import os
import sys
import operator

sys.path.insert(0, os.path.abspath(".."))

import trishula as T


def realnum(d):
    if "fractional" in d:
        return float(d["integer"] + "." + d["fractional"])
    return float(d["integer"])


term = (
    (
        (-(T.Value("-")) >= (lambda x: -1.0 if x is not None else 1.0))
        >> (
            T.Namespace(
                (T.Regexp("[1-9][0-9]*") @ "integer")
                >> -(T.Value(".") >> (T.Regexp("[0-9]*") @ "fractional"))
            )
            >= realnum
        )
    )
    >= (lambda x: x[0] * x[1])
) | (T.Value("0") >= float)

space = T.Value(" ")

parenthesis = T.Namespace(
    T.Value("(") >> (T.Ref(lambda: grammar) @ "value") >> T.Value(")")
) >= (lambda d: d["value"])


def op(string, fn):
    return T.Namespace(
        ((term | parenthesis) @ "_1")
        >> -space
        >> (T.Value(string) @ "operator")
        >> (-(-space >> (T.Ref(lambda: grammar) @ "grammar")))
    ) >= (lambda d: fn(d["_1"], d["grammar"]))


grammar = (
    op("*", operator.mul)
    | op("/", operator.truediv)
    | op("+", operator.add)
    | op("-", operator.sub)
    | parenthesis
    | term
)

items = (
    "0",
    "-123",
    "123",
    "1 / 2",
    "1 + 2 * -3 / 4",
    "1 + 2 / 2",
    "(1 + 2) * 3",
    "(1 - (2 - (3 - 4)))",
    "1.4 * 3",
)

for x in items:
    result = T.Parser().parse(grammar, x)
    print(vars(result))

# Result is:
#
#  {'status': <Status.SUCCEED: 1>, 'index': 1, 'value': 0.0, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 4, 'value': -123.0, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 3, 'value': 123.0, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 5, 'value': 0.5, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 14, 'value': -0.5, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 9, 'value': 2.0, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 11, 'value': 9.0, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 19, 'value': -2.0, 'namespace': {}}
#  {'status': <Status.SUCCEED: 1>, 'index': 7, 'value': 4.199999999999999, 'namespace': {}}
