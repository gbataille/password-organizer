from dataclasses import dataclass
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import Condition, IsDone
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import (
    FormattedTextControl, GetLinePrefixCallable, UIContent, UIControl
)
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.dimension import LayoutDimension as D
import string
from typing import Generic, List, Optional, TypeVar

from .common import default_style


T = TypeVar('T')


class Separator:
    """ Used just as a type. Not supposed to be instantiated """


@dataclass
class Choice(Generic[T]):
    display_text: str
    value: T
    disabled_reason: Optional[str] = None

    @property
    def is_disabled(self) -> bool:
        return self.disabled_reason is not None

    @property
    def display_length(self) -> int:
        return len(self.display_text)

    @staticmethod
    def separator() -> 'Choice':
        return Choice('-' * 15, Separator, '')

    @property
    def is_separator(self) -> bool:
        return self.value == Separator

    @staticmethod
    def from_string(value: str) -> 'Choice':
        return Choice(value, value, None)


class ChoicesControl(UIControl):
    """
    Menu to display some textual choices.
    Provide a search feature by just typing the start of the entry desired
    """
    def __init__(self, choices: List[Choice], **kwargs):
        self.selected_option_index = -1
        self.answered = False
        self.search_string: Optional[str] = None
        self.choices = choices
        self._init_choices(default=kwargs.pop('default'))
        super().__init__(**kwargs)

    def _init_choices(self, default=None):
        for i, choice in enumerate(self.choices):
            if choice.display_text == default:
                self.selected_option_index = i

            # First non disabled choice
            if self.selected_option_index == -1 and not choice.is_disabled:
                self.selected_option_index = i

    def preferred_width(self, max_available_width: int) -> int:
        max_elem_width = max(list(map(lambda x: x.display_length, self.choices)))
        return min(max_elem_width, max_available_width)

    def preferred_height(
        self,
        width: int,
        max_available_height: int,
        wrap_lines: bool,
        get_line_prefix: Optional[GetLinePrefixCallable],
    ) -> Optional[int]:
        return self.choice_count

    def create_content(self, width: int, height: int) -> UIContent:
        return UIContent(
            get_line=lambda i: self._get_line_tokens(i, self.choices[i]),
            line_count=self.choice_count,
        )

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_line_tokens(self, line_number, choice):
        tokens = []

        if self.search_string:
            if (
                choice.is_separator
                or (
                    isinstance(choice.display_text, str)
                    and not choice.display_text.startswith(self.search_string)
                )
            ):
                if line_number == self.selected_option_index:
                    # the current selection is masked, moving to the next visible entry
                    # FIXME: when no choices left to display, selection is out of bound
                    self.selected_option_index += 1
                return

        selected = (line_number == self.selected_option_index)

        if selected:
            tokens.append(('class:set-cursor-position', ' \u276f '))
        else:
            # For alignment
            tokens.append(('', '   '))

        if choice.is_disabled:
            token_text = choice.display_text
            if choice.disabled_reason:
                token_text += f' ({choice.disabled_reason})'
            tokens.append(('class:selected' if selected else 'class:disabled', token_text))
        else:
            try:
                tokens.append(('class:selected' if selected else '', str(choice.display_text)))
            except Exception:
                tokens.append(('class:selected' if selected else '', choice.display_text))

        return tokens

    def get_selection(self) -> Choice:
        return self.choices[self.selected_option_index]

    def get_search_string_tokens(self):
        if self.search_string is None:
            return None

        return [
            ('', '\n'),
            ('class:question-mark', '/ '),
            ('class:search', self.search_string),
            ('class:question-mark', '...'),
        ]

    def append_to_search_string(self, char: str) -> None:
        """ Appends a character to the search string """
        if self.search_string is None:
            self.search_string = ''
        self.search_string += char

    def remove_last_char_from_search_string(self) -> None:
        """ Remove the last character from the search string (~backspace) """
        if self.search_string and len(self.search_string) > 1:
            self.search_string = self.search_string[:-1]
        else:
            self.search_string = None


def question(message, choices: List[Choice], default=0, qmark='?', key_bindings=None, **kwargs):
    """
    Paramaters
    ==========
    kwargs: Dict[Any, Any]
        Any additional arguments that a prompt_toolkit.application.Application can take. Passed
        as-is
    """
    if key_bindings is None:
        key_bindings = KeyBindings()

    choices_control = ChoicesControl(choices, default=default)

    def get_prompt_tokens():
        tokens = []

        tokens.append(('class:question-mark', qmark))
        tokens.append(('class:question', ' %s ' % message))
        if choices_control.answered:
            tokens.append(('class:answer', ' ' + choices_control.get_selection().display_text))
        else:
            tokens.append(('class:instruction', ' (Use arrow keys)'))
        return tokens

    @Condition
    def has_search_string():
        return choices_control.get_search_string_tokens is not None

    # assemble layout
    layout = Layout(
        HSplit([
            Window(
                height=D.exact(1),
                content=FormattedTextControl(get_prompt_tokens)
            ),
            ConditionalContainer(
                Window(choices_control),
                filter=~IsDone()        # pylint:disable=invalid-unary-operand-type
            ),
            ConditionalContainer(
                Window(
                    height=D.exact(2),
                    content=FormattedTextControl(choices_control.get_search_string_tokens)
                ),
                filter=has_search_string
            ),
        ])
    )

    @key_bindings.add(Keys.ControlQ, eager=True)
    def exit_menu(event):
        event.app.exit(exception=KeyboardInterrupt())

    if not key_bindings.get_bindings_for_keys((Keys.ControlC,)):
        key_bindings.add(Keys.ControlC, eager=True)(exit_menu)

    @key_bindings.add(Keys.Down, eager=True)
    def move_cursor_down(_event):        # pylint:disable=unused-variable
        def _next():
            choices_control.selected_option_index = (
                (choices_control.selected_option_index + 1) % choices_control.choice_count)
        _next()
        while choices_control.choices[choices_control.selected_option_index].is_disabled:
            _next()

    @key_bindings.add(Keys.Up, eager=True)
    def move_cursor_up(_event):        # pylint:disable=unused-variable
        def _prev():
            choices_control.selected_option_index = (
                (choices_control.selected_option_index - 1) % choices_control.choice_count)
        _prev()
        while choices_control.choices[choices_control.selected_option_index].is_disabled:
            _prev()

    @key_bindings.add(Keys.Enter, eager=True)
    def set_answer(event):        # pylint:disable=unused-variable
        choices_control.answered = True
        choices_control.search_string = None
        event.app.exit(result=choices_control.get_selection().value)

    def search_filter(event):
        choices_control.append_to_search_string(event.key_sequence[0].key)

    for character in string.printable:
        key_bindings.add(character, eager=True)(search_filter)

    @key_bindings.add(Keys.Backspace, eager=True)
    def delete_from_search_filter(_event):        # pylint:disable=unused-variable
        choices_control.remove_last_char_from_search_string()

    return Application(
        layout=layout,
        key_bindings=key_bindings,
        mouse_support=True,
        style=default_style,
        **kwargs
    )
