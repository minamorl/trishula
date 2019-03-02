from enum import Enum, auto

class Status(Enum):
    SUCCEED = auto()
    FAILED = auto()


class Node:
    def __init__(self, status, index):
        self.status = status
        self.index = index

class OperatorMixin:
    def __rshift__(self, other):
        return Sequence(self, other)
    def __or__(self, other):
        return OrderedChoise(self, other)
    def __invert__(self):
        return ZeroOrMore(self)
    def __invert__(self):
        return ZeroOrMore(self)
    def __pos__(self):
        return OneOrMore(self)
    def __neg__(self):
        return Optional(self)


class Sequence(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            resultB = self.b.parse(target, resultA.index)
            return Node(Status.SUCCEED, resultB.index)
        return Node(Status.FAILED, i)


class OrderedChoise(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            return Node(Status.SUCCEED, resuluA.index)
        resultB = self.b.parse(target, resultA.index)
        if resultB.status is Status.SUCCEED:
            return Node(Status.SUCCEED, resultB.index)
        return Node(Status.FAILED, i)


class OneOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        return (self.a >> ZeroOrMore(self.a)).parse(target, i)


class ZeroOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.status is False or result.index == i:
            return Node(Status.SUCCEED, result.index)
        return self.parse(target, result.index)


class Optional(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        return Node(Status.SUCCEED, result.index)


class Value(OperatorMixin):
    def __init__(self, val):
        self.val = val
    def parse(self, target, i):
        if target[i:i + len(self.val)] == self.val:
            return Node(Status.SUCCEED, i + len(self.val))
        return Node(Status.FAILED, i)


class And(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        return Node(result.status, i)


class Not(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.status is Status.SUCCEED:
            return Node(Status.FAILED, i)
        return Node(Status.SUCCEED, i)


class Parser:
    def parse(self, grammar, string):
        result = grammar.parse(string, 0)
        return Node(Status.SUCCEED if result.index == len(string) else Status.FAILED, result.index)


grammar = Value("aaa") >> (Value("bbb") | Value("ccc")) >> +Value("eee") >> -Value("f") >> Value("g") >> Not(Value("hhh"))

print(vars(Parser().parse(grammar, "aaaccceeeeeefghhh")))
