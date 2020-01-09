"""
`password` type question
"""
from . import std_input


def question(message, **kwargs):
    kwargs['is_password'] = True
    return std_input.question(message, **kwargs)
