"""The main API module. """
from __future__ import absolute_import, print_function
from .compiler import State, SplitState, Match, compile
from .tokenizer import to_postfix


def update_states(current_states, state):
    if state in current_states:
        return
    elif isinstance(state, State) or state is Match:
        current_states.add(state)
    elif isinstance(state, SplitState):
        update_states(current_states, state.outs[0])
        update_states(current_states, state.outs[1])


def make_step(current_states, c):
    new_states = set()
    for state in current_states:
        if state is not Match and state.c == c:
            update_states(new_states, state.outs[0])
    return new_states


def match(pattern, s):
    """Apply a pattern to a string and return the result of the match.

    :param pattern: A POSIX-like regular expression.
    :type pattern: str

    :s: A string to match.
    :type s: str

    :returns: True if matches, False otherwise.
    :rtype: bool

    :raises: :py:class:`~MalformedRegex` if the regular expression is
      malformed.

    """
    postfix = to_postfix(pattern)
    state = compile(postfix)
    current_states = set()
    update_states(current_states, state)

    for c in s:
        current_states = make_step(current_states, c)

    return Match in current_states
