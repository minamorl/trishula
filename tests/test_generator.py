import trishula as T
from trishula.decorator import (
    generator_wrapper,
    collect_grammars,
    GeneratorResult,
    send_back,
    ResultEmurator,
    define_parser,
)

import unittest


def parser():
    yield T.Value("a")
    a = yield (T.Regexp(r"[a-z]") >> T.Value("b"))
    if a[0] == "a":
        raise GeneratorResult("found a")
    yield T.Value("a")
    raise GeneratorResult(a)


class TestGenerator(unittest.TestCase):
    def test_collect_grammars(self):
        p = generator_wrapper(parser())
        grammars = collect_grammars(p)
        self.assertEqual(len(grammars), 3)

    def test_send_back(self):
        p = generator_wrapper(parser())
        v = ["a", ["b", "a"], "a"]
        result = send_back(p, v)
        self.assertEqual(result, v[1])
        p = generator_wrapper(parser())
        v = ["a", ["a", "b"], "a"]
        result = send_back(p, v)
        self.assertEqual(result, "found a")

    def test_result_emurator(self):
        e = ResultEmurator()
        self.assertEqual(e["a"], e)
        self.assertEqual(e.a.b, e)
        self.assertEqual(e[1], e)

    def test_define_parser(self):
        p = define_parser(parser)
        self.assertEqual(p.parse("aaba", 0).value, "found a")
        self.assertEqual(p.parse("acba", 0).value, ["c", "b"])


if __name__ == "__main__":
    unittest.main()
