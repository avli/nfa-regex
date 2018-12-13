import pytest

from regex.tokenizer import to_postfix, Character, Concatenation, \
    Disjunction, Operator, square_brackets_expand
from regex.exceptions import MalformedRegex


def as_list_of_tokens(s):
    """A helper funcion that transforms a postfix form string to the list of
    corresponding tokens. Doesn't support all the cases but still useful."""
    lst = []
    for c in s:
        if c in '+?*':
            lst.append(Operator(c))
        elif c == '.':
            lst.append(Concatenation)
        elif c == '|':
            lst.append(Disjunction)
        else:
            lst.append(Character(c))
    return lst


# square_brackets_expand tests start -------------------

def test_square_brackets_expand_single_char():
    assert square_brackets_expand(['a']) == ['a']


def test_square_brackets_expand_simple_range():
    assert square_brackets_expand(['a', '-', 'c']) == ['a', 'b', 'c']


def test_square_brackets_expand_mixed_ex1():
    assert square_brackets_expand(
        ['a', 'b', 'x', '-', 'z', '4', '2']) == \
                ['a', 'b', 'x', 'y', 'z', '4', '2']


def test_square_brackets_expand_mixed_ex2():
    assert square_brackets_expand(['x', '-', 'z', 'a', 'b']) == \
        ['x', 'y', 'z', 'a', 'b']


def test_square_brackets_expand_dot():
    assert square_brackets_expand(['a', 'b', '-', '.']) == ['a']

# square_brackets_expand tests end -------------------


# to_postfix tests start -------------------

def test_plus_operator_only():
    with pytest.raises(MalformedRegex):
        to_postfix('+')


def test_three_plus_operators():
    with pytest.raises(MalformedRegex):
        to_postfix('+++')


def test_mixed_operators():
    with pytest.raises(MalformedRegex):
        to_postfix('???+*+++**?')


def test_incorred_mixed_operators_and_characters():
    with pytest.raises(MalformedRegex):
        to_postfix('a+???a+bc**')


def test_single_character():
    assert to_postfix('^a$') == as_list_of_tokens('a')


def test_two_characters():
    assert to_postfix('^ab$') == as_list_of_tokens('ab.')


def test_three_characters():
    assert to_postfix('^abc$') == as_list_of_tokens('ab.c.')


def test_four_characters():
    assert to_postfix('^abcd$') == as_list_of_tokens('ab.c.d.')


def test_one_character_plus():
    assert to_postfix('^a+$') == as_list_of_tokens('a+')


def test_one_character_star():
    assert to_postfix('^a*$') == as_list_of_tokens('a*')


def test_character_plus_in_the_middle():
    assert to_postfix('^ab+c$') == as_list_of_tokens('ab+.c.')


def test_character_star_in_the_middle():
    assert to_postfix('^ab*c$') == as_list_of_tokens('ab*.c.')


def test_one_character_question_mark():
    assert to_postfix('^a?$') == as_list_of_tokens('a?')


def test_one_character_question_mark_in_the_middle():
    assert to_postfix('^ab?c$') == as_list_of_tokens('ab?.c.')


def test_three_characters_with_pluses():
    assert to_postfix('^a+b+c+$') == as_list_of_tokens('a+b+.c+.')


def test_redundant_parenthesis():
    assert to_postfix('^a(b)$') == as_list_of_tokens('ab.')


def test_parenthesis_plus():
    assert to_postfix('^a(bc)+$') == as_list_of_tokens('abc.+.')


def test_folded_parenthesis():
    assert to_postfix('^a(b+(cd)+)$') == as_list_of_tokens('ab+cd.+..')


def test_incorrect_expression_in_parenthesis():
    with pytest.raises(MalformedRegex):
        to_postfix('^a(+++)b$')


def test_simple_alt():
    assert to_postfix('^a|b$') == as_list_of_tokens('ab|')


def test_alt_with_plus():
    assert to_postfix('^a+|b+$') == as_list_of_tokens('a+b+|')


def test_alt_with_groups():
    assert to_postfix('^(abc)|(cde)$') == as_list_of_tokens('ab.c.cd.e.|')

# to_postfix tests end -------------------
