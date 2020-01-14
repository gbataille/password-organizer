"""
`input` type question
"""
import inspect
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.validation import Validator, ValidationError

from .common import default_style


def question(message, **kwargs):
    validate_prompt = kwargs.pop('validate', None)

    if validate_prompt:
        if inspect.isclass(validate_prompt) and issubclass(validate_prompt, Validator):
            kwargs['validator'] = validate_prompt()
        elif callable(validate_prompt):

            class _InputValidator(Validator):

                def validate(self, document):
                    verdict = validate_prompt(document.text)

                    if verdict is True:
                        if verdict is False:
                            verdict = 'invalid input'
                        raise ValidationError(
                            message=verdict,
                            cursor_position=len(document.text))

            kwargs['validator'] = _InputValidator()

    qmark = kwargs.pop('qmark', '?')

    def _get_prompt_tokens():
        return [
            ('class:question-mark', qmark),
            ('class:question', ' %s  ' % message)
        ]

    session = PromptSession(
        message=_get_prompt_tokens(),
        lexer=SimpleLexer(style='class:answer'),
        style=default_style,
        **kwargs
    )

    return session.app
