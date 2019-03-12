import os
import sys
import operator
import pprint
import unittest as U

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


def replaceOperator(d, fn):
    d["operator"] = fn
    return d


def op(string, fn):
    return T.Namespace(
        ((term | parenthesis) @ "left")
        >> -space
        >> (T.Value(string) @ "operator")
        >> (-(-space >> (T.Ref(lambda: grammar) @ "right")))
    ) >= (lambda d: replaceOperator(d, fn))


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
    "1 / 2 / 2",
    "1 / 2 / 2 / 2 / 2",
    "1 * 2 / 3",
    "(1 + 2) * 3",
    "(1 - (2 - (3 - 4)))",
    "1.4 * 3",
    "(1 + (2 / 3))",
    "(2 * 3) / 4",
    "1 + 2 / 3",
    "((1)) * 2",
    "((1) / 2 / 3) * 5",
    "(-1 * (0 - (1 * 2) / 3) / 4 / 5) * 6 / 7",
    "1 - 1 - 1",
)


def rotation(d):
    if not isinstance(d, dict):
        return d

    return left_rotation(d)

def left_rotation(d):
    if not isinstance(d, dict):
        return d
    if isinstance(d["right"], float):
        if isinstance(d["left"], dict):
            d["left"] = left_rotation(d["left"])
            return d
        return d
    if d["operator"] is operator.add or d["operator"] is operator.sub and not isinstance(d["left"], float):
        return right_rotation(d)


    A = d["left"]
    B = d["right"]["left"]
    C = d["right"]["right"]
    P = d["operator"]
    Q = d["right"]["operator"]

    result = {"left": {"left": A, "operator": P, "right": B}, "operator": Q, "right": C}
    return left_rotation(result)


def right_rotation(d):
    if not isinstance(d, dict):
        return d
    if isinstance(d["left"], float):
        if isinstance(d["right"], dict):
            d["right"] = right_rotation(d["right"])
            return d
        return d
    A = d["left"]["left"]
    B = d["left"]["right"]
    C = d["right"]
    P = d["left"]["operator"]
    Q = d["operator"]

    result = {"left": A, "operator": P, "right": {"left": B, "operator": Q, "right": C}}
    return right_rotation(result)


def calc(d):
    if not isinstance(d, dict):
        return d
    left = calc(d["left"])
    right = calc(d["right"])
    return d["operator"](left, right)


for x in items:
    result = T.Parser().parse(grammar, x).value
    value = calc(rotation(result))
    if float(eval(x)) != value:
        pprint.pprint(((result)))
        pprint.pprint((rotation(result)))
        print(x)
        print(float(eval(x)))
        print(value)

        print()
    else:
        print(f"{x} is {calc(left_rotation(result))}")
