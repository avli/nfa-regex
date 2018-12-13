import string

import pytest

from regex import match
from regex.exceptions import MalformedRegex


def test_match_empty():
    assert match('', '')


def test_match_single_character():
    assert match('a', 'a')


def test_match_single_character_doest_match():
    assert not match('a', 'b')


def test_match_multiple_characters():
    assert match('abc', 'abc')


def test_match_multiple_characters_doesnt_match():
    assert not match('abc', 'abe')


def test_match_character_with_plus():
    assert match('a+', 'a' * 30)


def test_match_character_with_star_ex1():
    assert match('a*', 'a')


def test_match_character_with_star_ex2():
    assert match('a*', 'a'*30)


def test_match_character_with_caret():
    assert not match('^a', 'b')
    assert match('^^a', 'b')
    assert match('^a', 'a')


def test_match_multiple_characters_with_caret():
    assert match('^ab^c', 'abk')


def test_assert_range_with_caret():
    assert match('[^a-z]', 'A')
    assert match('[^a-z]+', 'ABC42')
    assert match('[^abc]+', 'cde')


def test_single_dot():
    assert match('.', 'a')
    assert match('.', 'b')
    assert match('.', '1')


def test_single_dot_with_caret():
    assert not match('^^.', 'a')
    assert not match('^^.', 'b')
    assert not match('^^.', '1')


def test_dot_with_star():
    assert match('.*', '')
    assert match('.*', 'foo')
    assert match('.*', 'foobar')


def test_escaped_dot():
    assert match(r'\.', '.')
    assert not match(r'\.', 'a')
    assert match(r'hello\.', 'hello.')
    assert not match(r'hello\.', 'hello!.')


def test_dot_in_the_middle():
    assert match('ab.d', 'abcd')
    assert match('ab.d', 'abZd')


def test_dot_in_range():
    assert match('[ab.]+', 'abc')
    assert match('[ab-.]+', 'aaa')
    with pytest.raises(MalformedRegex):
        match(r'[ab-\.]+', 'abZ')


def test_match_range_with_dot():
    assert match('[a.c]', 'ac')


def test_match_range_caret():
    assert not match('^[^abc]$', 'abc')
    assert not match('^[^abc]$', 'a')


def test_match_character_with_plus_in_the_middle():
    assert match('ab+c', 'abbbc')


def test_match_group_of_characters_with_plus_in_the_middle():
    assert match('a(bc)+d', 'abcbcd')


def test_match_group_of_characters_with_plus_in_the_middle_doesnt_match():
    assert not match('a(bc)+d', 'abcbcbd')


def test_match_single_character_question_mark():
    assert match('^a?', 'a')


def test_match_single_character_question_mark_doesnt_match():
    assert not match('^a?$', 'aa')


def test_complex_expression_ex1():
    assert not match('a(bc+(de+))f', 'abcbcdef')


def test_complex_expression_ex2():
    assert match('a(bc+(de+))f', 'abcdeeef')


def test_alt_two_symbols():
    assert match('a|b', 'a')
    assert match('a|b', 'b')
    assert not match('a|b', 'c')
    assert not match('a|a', 'b')


def test_alt_in_parenthesis_ex1():
    assert match('(ab|c)+d', 'ababcd')
    assert not match('(ab|c)+d', 'ababc')


def test_alt_in_parenthesis_ex2():
    assert match('(ab|c|d)+e', 'ababcdabcccde')
    assert not match('(ab|c|d)+e', 'abfe')


def test_alt_in_parenthesis_ex3():
    assert match('(a|b|c)+', 'abccccbbaabbbca')


def test_escape_operators():
    assert match('a\\+', 'a+')
    assert match('\\(\\)', '()')
    assert match('\\ab\\+', 'ab+')
    assert match('a+b*c\\+\\+d', 'aaac++d')
    assert not match('a+b*c\\+\\+d', 'aaac+d')
    assert match('\\[a-z\\]', '[a-z]')
    assert not match('\\[a-z\\]', 'a')


def test_match_email_address():
    literals = string.ascii_letters + string.digits
    literals = '|'.join(c for c in literals)
    # Not very accurate email regex though...
    pattern = '(%s)+@(%s)+\\.?(%s)*' % (literals, literals, literals)
    assert match(pattern, 'user@example.com')


def test_complex_pattern_ex1():
    pattern = r'[a-z0-9]*(!+|\?+)123'
    assert match(pattern, 'aaa000999zzzbbb???123')


def test_complex_pattern_ex2():
    pattern = r'[a-z0-9]*(!+|\?+)123(\?|&)+)'
    assert match(pattern, 'aaa000999zzzbbb???123&&&&&&&&&&&&&&&&???&&')


def test_complex_pattern_ex3():
    pattern = r'^([a-c]|[e-g][1-5]+)+$'
    assert match(pattern, 'bg424242ae424342')
    assert not match(pattern, 'bg424242ae426342')


def test_complex_pattern_ex4():
    pattern = r'^[([^&!!!!)]+$'
    assert match(pattern, '(((((((((^^^^^^!!!!!')


def test_complex_pattern_ex5():
    pattern = r'^((abc)|([1-3]|[7-9]))+$'
    assert match(pattern, '123abc123abc789789')
    assert not match(pattern, '123abc123abc789789ab')


# Test cases from
# https://en.wikibooks.org/wiki/Regular_Expressions/POSIX-Extended_Regular_Expressions

def test_metacharacters_dot():
    assert match('.', 'a')
    assert match('.', 'b')
    assert match('.', '*')
    assert match('.', '=')
    assert match('.', '1')
    assert match('.', '.')
    assert match('.+', 'abc123???!!!&&&VVVPPPQQQ+=100')


def test_metacharacters_brackets():
    assert match('[abc]', 'a')
    assert match('[abc]', 'b')
    assert match('[abc]', 'c')
    assert not match('[abc]', 'z')
    assert match('[a-z]', 'a')
    assert match('[a-z]', 'z')
    assert match('[a-z]', 'k')
    assert not match('[a-z]', 'A')
    assert not match('[a-z]', '8')
    assert match('[abcx-z]', 'a')
    assert match('[abcx-z]', 'y')
    assert not match('[abcx-z]', 'i')
    assert match('[a-cx-z]', 'b')
    assert match('[a-cx-z]', 'y')
    assert not match('[a-cx-z]', 'q')


def test_metacharacters_brackets_caret():
    assert not match('[^abc]', 'a')
    assert match('[^abc]', 'f')
    assert not match('[^a-z]', 'p')
    assert match('[^a-z]', 'P')
    assert match('[^a-z]', 'abc123abc')


def test_metacharacters_starting():
    assert match('^abc', 'abc')
    assert not match('^abc', 'zabc')


def test_metacharacters_ending():
    assert match('abc$', 'abc')
    assert not match('abc$', 'abcz')


def test_metacharacters_star():
    assert match('ab*c', 'ac')
    assert match('ab*c', 'abc')
    assert match('ab*c', 'abbbc')


def test_metacharacters_plus():
    assert not match('ab+c', 'ac')
    assert match('ab+c', 'abc')
    assert match('ab+c', 'abbbc')


def test_metacharacters_question_mark():
    assert match('ab?c', 'ac')
    assert match('ab?c', 'abc')


def test_metacharacters_pipe():
    assert match('abc|def', 'def')
    assert match('(abc)|(def)', 'abc')
    assert not match('^(abc)|(def)$', 'defabc')
