"""The NFA compiler module."""
from __future__ import absolute_import, print_function
from .tokenizer import Character, Concatenation, Disjunction, Operator


class State:
    def __init__(self, c):
        self.c = c
        self.outs = []

    def __repr__(self):
        return "State<%s> -> %s" % (self.c, self.outs[0])


class SplitState:
    def __init__(self):
        self.outs = []

    def __repr__(self):
        return "SplitState<%s>" % self.outs


class _Match:
    def __repr__(self):
        return "Match"
Match = _Match()  # Match state singleton.


class Fragment:
    """Represents an unfinished part of an NFA."""
    def __init__(self, start, dangling_arrows):
        self.start = start
        self.dangling_arrows = dangling_arrows


class DanglingArrow:
    """Reresents fragment outs that are not connected to any state."""
    def __init__(self, state, out_index):
        self.state = state
        self.out_index = out_index


# Compiler helper functions.


def connect(frag, state):
    """Connects all the dangling fragment outputs to a state.

    :param frag: An NFA fragment whose dangling arrows will be connected
      to the state.
    :type frag: :py:class:`~Fragment`

    :state: A state that should be the out for the fragment dangling arrows.
    :type state: :py:class:`State`

    """
    while(frag.dangling_arrows):
        arrow = frag.dangling_arrows.pop()
        arrow.state.outs[arrow.out_index] = state


def is_character(obj):
    return isinstance(obj, Character)


def is_operator(obj):
    return isinstance(obj, Operator)


def is_concatenation(obj):
    return obj is Concatenation


def is_disjunction(obj):
    return obj is Disjunction


def compile(pattern):
    """Compile the postfix form of a regular expression to an NFA.

    :param pattern: A list representing the postfix form of
      a regular expression. Output of the
      :py:func:`~regex.preprocessor.to_postfix` function.
    :type pattern: list

    :returns: The starting state of the regular expression NFA.
    :rtype: :py:class:`~State`

    Example:

    .. code: python

      >>> compile('ab+')
      State<b> -> SplitState<[State<b> -> SplitState<[...]>, Match]>

    """
    stack = []
    for token in pattern:
        if is_character(token):
            state = State(token)
            state.outs.append(None)
            dangling_arrows = [
                DanglingArrow(state, 0)
            ]
            frag = Fragment(state, dangling_arrows)
            stack.append(frag)
        elif is_concatenation(token):
            prev_frag_2 = stack.pop()
            prev_frag_1 = stack.pop()
            connect(prev_frag_1, prev_frag_2.start)
            frag = Fragment(prev_frag_1.start, prev_frag_2.dangling_arrows)
            stack.append(frag)
        elif is_disjunction(token):
            prev_frag_2 = stack.pop()
            prev_frag_1 = stack.pop()
            state = SplitState()
            state.outs.append(prev_frag_1.start)
            state.outs.append(prev_frag_2.start)
            dangling_arrows = prev_frag_1.dangling_arrows \
                + prev_frag_2.dangling_arrows
            frag = Fragment(state, dangling_arrows)
            stack.append(frag)
        # If we are here, the token is an operator.
        elif token.op == '+':
            prev_frag = stack.pop()
            state = SplitState()
            state.outs.append(prev_frag.start)  # The first out is cycle.
            state.outs.append(None)  # The second out should be connected
                                     # to the next fragment.
            connect(prev_frag, state)
            dangling_arrows = [
                DanglingArrow(state, 1)
            ]
            frag = Fragment(prev_frag.start, dangling_arrows)
            stack.append(frag)
        elif token.op == '*':
            prev_frag = stack.pop()
            state = SplitState()
            state.outs.append(prev_frag.start)
            connect(prev_frag, state)
            state.outs.append(None)
            dangling_arrows = [
                DanglingArrow(state, 1)
            ]
            frag = Fragment(state, dangling_arrows)
            stack.append(frag)
        elif token.op == '?':
            prev_frag = stack.pop()
            state = SplitState()
            state.outs.append(prev_frag.start)
            state.outs.append(None)
            dangling_arrows = prev_frag.dangling_arrows
            dangling_arrows.append(DanglingArrow(state, 1))
            frag = Fragment(state, dangling_arrows)
            stack.append(frag)

    if stack:
        frag = stack.pop()
        connect(frag, Match)
        return frag.start
