from .grammar import _FnWrapper, Success


def define_parser(fn):
    def parse(s, i):
        a = generator_wrapper(fn())
        b = generator_wrapper(fn())
        grammars = collect_grammars(a)
        results = [None]
        current_index = i
        for p in grammars:
            result = p.parse(s, current_index)
            current_index = result.index
            if not result.isSuccess():
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
    for x in generator:
        grammars.append(x)
    grammars = grammars[:-1]
    return grammars


def send_back(generator, results):
    next(generator)
    x = None
    for r in results:
        x = generator.send(r)
    # retrive final value
    return x
