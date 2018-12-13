"""The module where the custom library exceptions live."""


class MalformedRegex(Exception):
    """Exception to be raise when the library can't parse
    a regular expression."""
    pass
