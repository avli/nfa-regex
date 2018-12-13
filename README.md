[![CircleCI](https://circleci.com/gh/avli/nfa-regex.svg?style=svg)](https://circleci.com/gh/avli/nfa-regex)
## Intro

The library implements a regular expression engine based on nondeterministic
finite automata (NFA). It uses the [Thompson's
construction](https://en.wikipedia.org/wiki/Thompson%27s_construction)
algorithm to transform regular expressions into NFAs. No backreferences are used
during the matching process which should make this engine much faster than the
standard Python's `re` module.

Supported features:

- common operators like `*`, `+`, `?`, and `|`
- ranges, e.g. `[a-z]`
- groups, e.g. `(abc)`
- starting and ending position indicators: `^` and `$`
- the caret `^` operator

## How to Install

Prerequisites:

- Python version 3.6.6
- [virtualenv](https://virtualenv.pypa.io/en/latest/) or Python 3 `venv`
  module (optional)

Create a virtual environment with `virtualenv` or `venv` in the directory with
the library sources:

```console
$ virtualenv venv  # virtualenv approach
```

or

```console
$ python -m venv venv  # venv approach
```

Activate the environment with

```console
$ . ./venv/bin/activate
```

and install the library

```console
$ python setup.py install
```

## Running Tests

To check the installation was successful, it will be a good idea to run the
tests. The library uses pytest as a testing framework. If you've followed the
instructions from the previous section, pytest is already installed in your
virtual environment.

To run the tests do

```console
$ pytest tests/
```

To get a test coverage report run

```console
$ pytest --cov=regex tests/
```

A test coverage example report:

```
---------- coverage: platform darwin, python 3.6.6-final-0 -----------
Name                                                                       Stmts   Miss  Cover
----------------------------------------------------------------------------------------------
venv/lib/python3.6/site-packages/regex-0.1-py3.6.egg/regex/__init__.py         3      0   100%
venv/lib/python3.6/site-packages/regex-0.1-py3.6.egg/regex/compiler.py        92      4    96%
venv/lib/python3.6/site-packages/regex-0.1-py3.6.egg/regex/exceptions.py       2      0   100%
venv/lib/python3.6/site-packages/regex-0.1-py3.6.egg/regex/executor.py        25      0   100%
venv/lib/python3.6/site-packages/regex-0.1-py3.6.egg/regex/tokenizer.py      177     14    92%
----------------------------------------------------------------------------------------------
TOTAL                                                                        299     18    94%
```

## API

The API is simple and consists of one function named `match`. The function
takes a POSIX-like regular expression and a string and returns `True` or
`False` depending on whether the string matcher the expression or not.

```python
>>> from regex import match
>>> match(r'a|b', 'a')
True
>>> match(r'[a-z0-9]*(!+|\?+)123', 'aaa000999zzzbbb???123')
True
>>> match(r'foo', 'bar')
False
```

The function raises the `MalformedRegex` exception if the regular expression
can't be parsed.

## Command Line Tool

The library ships with the command line tool named `regex`. It is a simple
app that takes a regular expression as its first argument and a string as
the second. For example:

```console
$ regex "a?a?b" "ab"
The string 'ab' matches
```

## References

[Regular Expression Matching Can Be Simple And
Fast](https://swtch.com/~rsc/regexp/regexp1.html) by Russ Cox.
