# Trishula - The modern parser combinator for Python 3

Trishula is a parser combinator library extended PEG syntaxes, inspired by Parsimmon(ES) and boost::spirit::qi(C++).

Trishula supports python version >= 3.7.0

## Examples

```python
grammar = (
    Value("aaa")
    >> (Value("bbb") | Value("ccc"))
    >> (+Value("eee") >= (lambda x: "modified"))
    >> -Value("f")
    >> Value("g")
    >> Regexp(r"a+")
    >> Not(Value("hhh"))
)
# This works
print(vars(Parser().parse(grammar, "aaaccceeeeeeeeeeeefgaaa")))

# {
#      'status': <Status.SUCCEED: 1>,
#      'index': 23,
#      'value': [[[[[['aaa', 'ccc'], 'modified'], 'f'], 'g'], 'aaa'], None]
# }
```

You can see examples in ["example" directory](https://github.com/minamorl/trishula/blob/master/example) (execute it under example directory). 

## Description

Grammers can be defined by **Value** and **Regexp** primitive and operators. Below we describe operators.

## Operators

As mentioned above, Trishula uses many operator overloads to make definition of parsers be easier.

| operator | result |
----|---- 
| >> | Sequence |
| \| | OrderedChoise |
| ~ | ZeroOrMore |
| + | OneOrMore |
| - | Optional |
| >= | Map |
| @ | NamedParser |

and we have classes named **Not** and **And**, which are made for prediction.


## Recursion

Trishula supports recursion with `Ref`. Recursion can be written like this:

```python
def grammar():
   return (
        (Value("[]") >= (lambda x: [])) |
        ((
            Value("[") >>
            Ref(grammar) >>
            Value("]")
        ) >= (lambda x: [x[0][1]]))
    )

def main():
    result = Parser().parse(grammar(), "[[[]]]")
    print(vars(result))
    # => {'status': <Status.SUCCEED: 1>, 'index': 6, 'value': [[[]]]}
```

Be aware that `Ref` executes function only once so that parser can be memorized.

## Namespace

Namespace is one of Trishula's powerful features. You can name your parser and retrieve values with map (as dict).

Usage is simple. Mark the parser with `@` operator like `parser @ "name"` and surround with `Namespace(parser)`. Then you can grab values with `Namespace(parser) => fn`. fn is a callable taking dict type and returns new value. 

```python
import trishula as T


def main():
    grammar = T.Namespace(
        T.Value("[") >> (T.Regexp(r"[0-9]+") >= (float)) @ "value" >> T.Value("]")
    ) >= (lambda a_dict: a_dict["value"])
    result = T.Parser().parse(grammar, "[12345]")
    print(vars(result))
    # ==> {'status': <Status.SUCCEED: 1>, 'index': 7, 'value': 12345.0, 'namespace': {}}


main()
```

Note that after mapped function called, internal namespace is cleaned up with empty dict.


## Conditional parsing

You can do something like this:
```python
def main():
    def cond(value):
        d = {
            "(": ")",
            "{": "}",
            "[": "]",
        }
        return T.Value(d.get(value[0]))


    grammar = T.Namespace(
        T.Value("[")
        >> +(T.Regexp(r"[a-z]") | T.Value("\n")) @ "value"
        >> T.Conditional(cond)
    )
    result = T.Parser().parse(grammar, "[abcd\n\nefg]")
    print(result)


main()
```

`Conditional` take one argument that receive a value and return parser. It runs dynamically so that you can choose a parser at runtime.


## Utils

There are `sep_by`, `sep_by1`, and `index`.

## Generator

```
import trishula as T


@T.define_parser
def parser():
    yield T.Value("aaa")
    v = yield T.Value("bbb")
    yield T.Value("ccc")
    # Do not forget to return a value
    yield v

print(T.Parser().parse(parser, "aaabbbccc"))
# ==> <Success index='9' value='bbb' namespace='{}'>
```
