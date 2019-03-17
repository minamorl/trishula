import re
from collections import namedtuple

Index = namedtuple("Index", ("offset", "line", "column"))


class Success:
    def __init__(self, index, value=None, namespace=None):
        self.index = index
        self.value = value
        self.namespace = namespace or dict()

    def isSuccess(self):
        return True

    def __repr__(self):
        return f"<Success index='{self.index}' value='{self.value}' namespace='{self.namespace}'>"


class Failure:
    def __init__(self, index, message=None):
        self.index = index
        self.message = message

    def isSuccess(self):
        return False

    def __repr__(self):
        return f"<Failure index='{self.index}' message='{self.message}'>"


class OperatorMixin:
    def __rshift__(self, other):
        if isinstance(other, Conditional):
            return ConditionalSequence(self, other)
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


class Conditional(OperatorMixin):
    def __init__(self, condition):
        self.condition = condition

    def parse(self, target, i, result):
        parser = self.condition(result)
        return parser.parse(target, i)


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
        if result.isSuccess():
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
        if resultA.isSuccess():
            resultB = self.b.parse(target, resultA.index)
            if resultB.isSuccess():
                namespace = resultA.namespace
                namespace.update(resultB.namespace)
                return Success(resultB.index, [resultA.value, resultB.value], namespace)
        return Failure(i)


class ConditionalSequence(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.isSuccess():
            resultB = self.b.parse(target, resultA.index, resultA.value)
            if resultB.isSuccess():
                namespace = resultA.namespace
                namespace.update(resultB.namespace)
                return Success(resultB.index, [resultA.value, resultB.value], namespace)
        return Failure(i)


class OrderedChoice(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.isSuccess():
            return resultA
        resultB = self.b.parse(target, resultA.index)
        if resultB.isSuccess():
            return resultB
        return Failure(i)


class OneOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = (self.a >> ZeroOrMore(self.a)).parse(target, i)
        if result.isSuccess():
            result.value = [result.value[0], *result.value[1]]
        return result


class ZeroOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i, values=None):
        values = values or []
        result = self.a.parse(target, i)
        if result.index == i:
            return Success(result.index, values)
        values.append(result.value)
        return self.parse(target, result.index, values)


class Optional(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.isSuccess():
            return Success(result.index, result.value, result.namespace)
        return Success(result.index)


class Value(OperatorMixin):
    def __init__(self, val):
        self.val = val

    def parse(self, target, i):
        if target[i : i + len(self.val)] == self.val:
            return Success(i + len(self.val), self.val)
        return Failure(i)


class And(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = self.a.parse(target, i)
        result.index = i
        return result


class Not(OperatorMixin):
    def __init__(self, a):
        self.a = a

    def parse(self, target, i):
        result = self.a.parse(target, i)
        epsParser = Value("")
        if result.isSuccess():
            return Failure(i)
        return Success(i, result.value, result.namespace)


class Map(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.isSuccess():
            result.value = self.b(result.value)
        return result


class NamespaceMap(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.isSuccess():
            return Success(result.index, self.b(result.namespace), {})
        return Failure(result.index)


class FlatMap(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def parse(self, target, i):
        result = self.a.parse(target, i)
        return self.b(result)


class Regexp(OperatorMixin):
    def __init__(self, regexp):
        self.regexp = regexp

    def _anchored(self, regexp):
        regexp = f"^{self.regexp}"
        return regexp

    def parse(self, target, i):
        regexp = self._anchored(self.regexp)
        matched = re.match(regexp, target[i:])
        if matched:
            return Success(i + matched.end(), matched.group())
        return Failure(i)


class _FnWrapper(OperatorMixin):
    def __init__(self, fn):
        self.fn = fn

    def parse(self, target, i):
        return self.fn(target, i)


def _index(target, i):
    splitted = target[:i].split("\n")
    line = len(splitted)
    column = len(splitted[-1]) + 1
    return Success(i, Index(i, line, column))


index = _FnWrapper(_index)


def sep_by1(content, separator):
    single = content >= (lambda x: [x])
    another = (separator >> content) >= (lambda x: x[1])
    multi = (content >> +another) >= (lambda x: [x[0], *x[1]])
    return multi | single


def sep_by(content, separator):
    return sep_by1(content, separator) | (T.Value("") >= (lambda _: []))


class Parser:
    def parse(self, grammar, string):
        result = grammar.parse(string, 0)
        if result.index == len(string):
            return Success(result.index, result.value)
        return Failure(result.index)
