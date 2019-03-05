# Trishula - The modern parser combinator for Python 3

Trishula is a parser combinator library extended PEG syntaxes, inspired by Parsimmon(ES) and boost::spirit::qi(C++).

Trishula supports python version >= 3.7.0

## Examples

```python
grammar = (
    Value("aaa")
    >> (Value("bbb") | Value("ccc"))
    >> (+Value("eee") @ (lambda x: Node(x.status, x.index, "modified")))
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
