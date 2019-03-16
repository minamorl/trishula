from enum import Enum, auto
import re


class Status(Enum):
    SUCCEED = auto()
    FAILED = auto()


class Node:
    def __init__(self, status, index, value=None, namespace=None):
        self.status = status
        self.index = index
        self.value = value
        self.namespace = namespace or dict()


class OperatorMixin:
    def __rshift__(self, other):
        return Sequence(self, other)

    def __or__(self, other):
        return OrderedChoice(self, other)

    def __invert__(self):
        return ZeroOrMore(self)

    def __pos__(self):
        return OneOrMore(self)

    def __neg__(self):
        return Optional(self)

    def __ge__(self, other):
        return Map(self, other)

    def __matmul__(self, other):
        return NamedParser(self, other)


class Ref(OperatorMixin):
    def __init__(self, ref):
        self.ref = ref
        self.parser = None

    def parse(self, target, i):
        if self.parser is None:
            self.parser = self.ref()
        return self.parser.parse(target, i)


class NamedParser(OperatorMixin):
    def __init__(self, parser, name):
        self.parser = parser
        self.name = name

    def parse(self, target, i):
        result = self.parser.parse(target, i)
        result.namespace[self.name] = result.value
        return result


class Namespace(OperatorMixin):
    def __init__(self, parser):
        self.parser = parser

    def parse(self, target, i):
        result = self.parser.parse(target, i)
        return result

    def __ge__(self, other):
        return NamespaceMap(self, other)


class Sequence(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            resultB = self.b.parse(target, resultA.index)
            if resultB.status is Status.SUCCEED:
                namespace = resultA.namespace
                namespace.update(resultB.namespace)
                return Node(
                    Status.SUCCEED,
                    resultB.index,
                    [resultA.value, resultB.value],
                    namespace,
                )
        return Node(Status.FAILED, i)


class OrderedChoice(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            return Node(Status.SUCCEED, resultA.index, resultA.value, resultA.namespace)
        resultB = self.b.parse(target, resultA.index)
        if resultB.status is Status.SUCCEED:
            return Node(Status.SUCCEED, resultB.index, resultB.value, resultB.namespace)
        return Node(Status.FAILED, i)


class OneOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = (self.a >> ZeroOrMore(self.a)).parse(target, i)
        if result.status == Status.SUCCEED:
            result.value = [result.value[0], *result.value[1]]
        return result


class ZeroOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i, values=None):
        values = values or []
        result = self.a.parse(target, i)
        if result.status is False or result.index == i:
            return Node(Status.SUCCEED, result.index, values, result.namespace)
        values.append(result.value)
        return self.parse(target, result.index, values)


class Optional(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = self.a.parse(target, i)
        return Node(Status.SUCCEED, result.index, result.value, result.namespace)


class Value(OperatorMixin):
    def __init__(self, val):
        self.val = val

    def parse(self, target, i):
        if target[i : i + len(self.val)] == self.val:
            return Node(Status.SUCCEED, i + len(self.val), self.val)
        return Node(Status.FAILED, i)


class And(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = self.a.parse(target, i)
        return Node(result.status, i, result.value, result.namespace)


class Not(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = self.a.parse(target, i)
        epsParser = Value("")
        if result.status is Status.SUCCEED:
            return Node(Status.FAILED, i)
        return Node(Status.SUCCEED, i, result.value, result.namespace)


class Map(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.status is Status.SUCCEED:
            result.value = self.b(result.value)
        return result


class NamespaceMap(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.status is Status.SUCCEED:
            result.value = self.b(result.namespace)
        return Node(result.status, result.index, result.value, {})


class FlatMap(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        result = self.a.parse(target, i)
        return self.b(result)


class Regexp(OperatorMixin):
    def __init__(self, regexp):
        if isinstance(regexp, re.Pattern):
            regexp = regexp.pattern
        self.regexp = regexp

    def _anchored(self, regexp):
        regexp = f"^{self.regexp}"
        return regexp

    def parse(self, target, i):
        regexp = self._anchored(self.regexp)
        matched = re.match(regexp, target[i:])
        if matched:
            return Node(Status.SUCCEED, i + matched.end(), matched.group())
        return Node(Status.FAILED, i)


class Parser:
    def parse(self, grammar, string):
        result = grammar.parse(string, 0)
        return Node(
            Status.SUCCEED if result.index == len(string) else Status.FAILED,
            result.index,
            result.value,
        )
