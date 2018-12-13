"""The tokenizer module contains classes and functions for
tramsforming regular expressions to their postfix form.
"""
from __future__ import absolute_import, print_function
from .exceptions import MalformedRegex


class Character:
    """A character token representation. Instances of this class can be
    compared with strings. The comparison logic is defined by the additional
    parameters passed to the constructor.

    :param c: A character the object represents.
    :type c: str

    :param caret: A flag defining if the character was preceeded by
      the caret. If it is True, the comparison logic will be inverted.
      Say ``c`` is 'a' and ``caret`` is True. Than this token equals anything
      but 'a'.
    :type caret: bool

    :param dot: Whether the "dot" logic should be applied during comparison.
      If this parameter is True, the character
      will match anything. Note that if ``c`` is '.' and dot is False,
      the character behaves like an escaped dot.
    :type dot: bool

    """
    def __init__(self, c, caret=False, dot=False):
        self.c = c
        self.caret = caret
        self.dot = dot

    def __eq__(self, other):
        if isinstance(other, Character):
            return self.c == other.c and self.caret == self.caret \
                and self.dot == other.dot
        elif isinstance(other, str):
            result = self.c == other
            if self.dot:
                result = True
            return result if not self.caret else not result
        else:
            raise NotImplemented

    def __repr__(self):
        if self.caret:
            return "Character<^%s>" % self.c
        else:
            return "Character<%s>" % self.c


class Range(Character):
    """A special case of a character that represents a range of characeters.
    A single character can be compared with a range instance. For example,
    if the character is in the range and it's not a caret range
    the result is True. This consistensy between characters and ranges makes
    implementation of the state machinea lot easier.

    :param caret: Whether the range in the regular expression was preceeded by
      the caret. This inverts the comparison behavior.
    :type caret: bool

    """
    def __init__(self, caret=False):
        super(Range, self).__init__(None, caret, False)
        self.chars = set()

    def add_char(self, c):
        self.chars.add(c)

    def __eq__(self, other):
        if isinstance(other, Range):
            return self.chars == other.chars
        elif isinstance(other, str):
            result = other in self.chars
            return result if not self.caret else not result

    def __repr__(self):
        return '^Range<%s>' % self.chars if self.caret \
            else 'Range<%s>' % self.chars


class _Concatenation:
    def __repr__(self):
        return "Concatenation"
Concatenation = _Concatenation()  # Concatenation singleton.


class _Disjunction:
    def __repr__(self):
        return "Disjunction"
Disjunction = _Disjunction()  # Disjunction singleton.


class Operator:
    """An operator token representation.

    :param op: An operator the object represents.
    :type op: str

    """
    def __init__(self, op):
        self.op = op

    def __eq__(self, other):
        return self.op == other.op

    def __repr__(self):
        return "Operator<%s>" % self.op


def square_brackets_expand(expr):
    """A helper function for expanding expressions in square brackets.

    :param expr: A list of characters in square brackets,
      e.g. ['a', '-', 'b']
    :type expr: list

    :returns: The expanded version of the expression.
    :rtype: list

    Example usage:

    .. code: python

      >>> square_brackets_expand(['a', '-', 'c'])
      ['a', 'b', 'c']

    """
    k = 0
    tokens = []
    result = []

    while k < len(expr):
        tokens.append(expr[k])
        if len(tokens) == 3 and tokens[1] == '-':
            # This is a range like a-z.
            start, end = tokens[0], tokens[2]
            for i in range(ord(start), ord(end) + 1):
                result.append(chr(i))
            tokens = []
        elif len(tokens) == 3:
            # No dash in the middle. We can safely expand the first character.
            result.append(tokens[0])
            tokens = tokens[1:]
        k += 1
    else:
        if tokens:
            result.extend(tokens)
    return result


def make_range(buf):
    caret = buf[0] == '^'
    range_ = Range(caret)
    buf = buf[1:] if caret else buf
    chars = square_brackets_expand(buf)
    for c in chars:
        range_.add_char(c)
    return range_


def add_anchors(pattern):
    """If there's no explicit start and end line symbols it is necessary to
    add the corresponding regexes to the beggining and end of the string.

    :param pattern: A regular expression.
    :type pattern: str

    """
    # Start line.
    pattern = pattern[1:] if pattern.startswith('^') else '.*' + pattern
    # End line.
    pattern = pattern[:-1] if pattern.endswith('$') else pattern + '.*'

    return pattern


def to_postfix(pattern):
    """Transform a regular expression to the postfix form.

    :param pattern: A regular expression.
    :type pattern: str

    :returns: A list of postfix form tokens for the given regular expression.
    :rtype: list

    :raises: :py:class:`~MalformedRegex` if the regular expression
      is malformed.

    """
    pattern = add_anchors(pattern)
    return _to_postfix(pattern)


def _to_postfix(pattern):
    stack = []
    natoms = 0
    in_paren = False
    buf = []
    nopenparen = 0
    nalt = 0
    escape = False
    caret = False
    in_brackets = False  # Whether we are in square brackets.
    range_buf = []  # Buffer for storing characters from square brackets.
    for c in pattern:
        if in_brackets:
            # Everything in square brackets must be treated literally.
            # Backslashes are not allowed.
            if c == '\\':
                raise MalformedRegex(
                    'Backslashes are not allowed in square brackets.')
            elif c == ']':
                range_ = make_range(range_buf)
                if natoms > 1:
                    stack.append(Concatenation)
                    natoms -= 1
                stack.append(range_)
                natoms += 1
                in_brackets = False
                continue
            else:
                range_buf.append(c)
        elif c == '\\':
            if in_paren:
                buf.append(c)
            else:
                escape = True
        elif escape:
            # If the previous symbol was escape, simply add whatever goes
            # next to the stack.
            if in_paren:
                buf.append(c)
            else:
                if natoms > 1:
                    stack.append(Concatenation)
                    natoms -= 1
                stack.append(Character(c, caret))
                caret = False
                natoms += 1
            escape = False
            continue
        elif in_paren and c != ')':
            # Accumulating symbols in parenthesis
            # before applying the postfix transform to them.
            if c == '(':
                nopenparen += 1
            buf.append(c)
            continue
        elif c == '^':
            caret = True
        elif c in '+*?':
            if natoms == 0:
                raise MalformedRegex()
            if isinstance(stack[-1], Operator):
                # Two operators one by one signal about a malformed regex.
                raise MalformedRegex()
            stack.append(Operator(c))
        elif c == '|':
            if natoms == 0:
                raise MalformedRegex()
            natoms -= 1
            while natoms:
                stack.append(Concatenation)
                natoms -= 1
            nalt += 1
        elif c == '(':
            # A group starts.
            in_paren = True
            nopenparen += 1
        elif c == ')':
            nopenparen -= 1
            # Handling the nested parentheses case.
            if nopenparen != 0:
                buf.append(')')
                continue
            in_paren = False
            expr = _to_postfix(''.join(buf))
            if expr is None:
                # Incorrect expression in parenthesis,
                # nothing we can do.
                raise MalformedRegex()
            buf = []
            if natoms > 1:
                stack.append(Concatenation)
                natoms -= 1
            stack.extend(expr)
            natoms += 1
        elif c == '[':
            in_brackets = True
            continue
        else:
            # Iterpret a character as a regular symbol.
            if natoms > 1:
                stack.append(Concatenation)
                natoms -= 1
            character = Character(c, caret, c == '.')
            stack.append(character)
            caret = False
            natoms += 1

    if natoms > 1:
        stack.append(Concatenation)
    while nalt:
        stack.append(Disjunction)
        nalt -= 1
    return stack
