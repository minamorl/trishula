from .grammar import _FnWrapper, Success
import sys

class ResultEmurator:
    def __len__(self):
        return sys.maxsize
    def __getattr__(self, key):
        return self
    def __getitem__(self, key):
        return self


class GeneratorResult(Exception):
    def __init__(self, result):
        super().__init__(f"Generator result is {result}")
        self.result = result


class GeneratorError(Exception):
    def __init__(self, result):
        pass


def define_parser(fn):
    def parse(s, i):
        a = generator_wrapper(fn())
        b = generator_wrapper(fn())
        grammars = collect_grammars(a)
        results = []
        current_index = i
        for p in grammars:
            result = p.parse(s, current_index)
            current_index = result.index
            if not result.is_success():
                return result
            results.append(result.value)
        return Success(current_index, send_back(b, results))

    return _FnWrapper(parse)


def generator_wrapper(generator):
    # to receive first sended value
    yield
    yield from generator


def collect_grammars(generator):
    next(generator)
    grammars = []
    try:
        while True:
            grammars.append(generator.send(ResultEmurator()))
    except GeneratorResult as e:
        pass
    return grammars


def send_back(generator, results):
    next(generator)
    next(generator)
    x = None
    try:
        i = 0
        while True:
            x = generator.send(results[i])
            i += 1
    except GeneratorResult as e:
        return e.result
    else:
        raise GeneratorError(
            "Parser cannot find a result. Raise GeneratorResult to return values."
        )
