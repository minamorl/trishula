# Trishula - The modern parser combinator for Python 3

Trishula is a parser combinator library extended PEG syntaxes, inspired by Parsimmon(ES) and boost::spirit::qi(C++).

## Examples

```python
grammar = (
    Value("aaa")
    >> (Value("bbb") | Value("ccc"))
    >> +Value("eee")
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
#      'value': [[[[[['aaa', 'ccc'], ['eee', 'eee', 'eee', 'eee']], 'f'], 'g'], 'aaa'], None]
# }
```

## Description

Grammers can be defined by **Value** primitive and operators. Below we describe operators.

## Operators

As mentioned avobe, Trishula uses many operator overloads to make definition of parsers be easier.

| operator | result |
----|---- 
| >> | Sequence |
| \| | OrderedChoise |
| ~ | ZeroOrMOre |
| + | OneOrMore |
| - | Optional |

and we have classes named **Not** and **And**, which are made for prediction.
