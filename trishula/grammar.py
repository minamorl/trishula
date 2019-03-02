from enum import Enum, auto

class Status(Enum):
    SUCCEED = auto()
    FAILED = auto()


class Node:
    def __init__(self, status, index):
        self.status = status
        self.index = index

class Sequence:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            resultB = self.b.parse(target, resultA.index)
            return Node(Status.SUCCEED, resultB.index)
        return Node(Status.FAILED, i)

class Value:
    def __init__(self, val):
        self.val = val
    def parse(self, target, i):
        if target[i:i + len(self.val)] == self.val:
            return Node(Status.SUCCEED, i + len(self.val))
        return Node(Status.FAILED, i)
    def __rshift__(self, other):
        return Sequence(self, other)


class Parser:
    def parse(self, grammar, string):
        return grammar.parse(string, 0)


grammar = Value("aaa") >> Value("bbb")

print(vars(Parser().parse(grammar, "aaabbb")))
