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
        # Selection to keep consistent
        self._selected_choice: Optional[Choice] = None
        self._selected_index: int = -1

        self.answered = False
        self._search_string: Optional[str] = None
        self._choices = choices
        self._init_choices(default=kwargs.pop('default'))
        self._cached_choices: Optional[List[Choice]] = None
        super().__init__(**kwargs)

    def _init_choices(self, default=None):
        if default is not None and default not in self._choices:
            # TODO - gbataille: exception logic
            raise Exception("")

        self._compute_available_choices(default=default)

    def _get_available_choices(self) -> List[Choice]:
        if self._cached_choices is None:
            self._compute_available_choices()

        return self._cached_choices or []

    def _compute_available_choices(self, default: Optional[Choice] = None) -> None:
        self._cached_choices = []

        for choice in self._choices:
            if self._search_string:
                if choice.display_text.startswith(self._search_string):
                    self._cached_choices.append(choice)
            else:
                self._cached_choices.append(choice)

        if self._cached_choices == []:
            self._selected_choice = None
            self._selected_index = -1
        else:
            if default is not None:
                self._selected_choice = default
                self._selected_index = self._cached_choices.index(default)

            if self._selected_choice not in self._cached_choices:
                self._selected_choice = self._cached_choices[0]
                self._selected_index = 0

    def _reset_cached_choices(self) -> None:
        self._cached_choices = None

    def get_selection(self):
        return self._selected_choice

    def select_next_choice(self) -> None:
        if not self._cached_choices or self._selected_choice is None:
            return

        def _next():
            self._selected_index += 1
            self._selected_choice = self._cached_choices[self._selected_index % self.choice_count]

        _next()
        while self._selected_choice.is_disabled:
            _next()

    def select_previous_choice(self) -> None:
        if not self._cached_choices or self._selected_choice is None:
            return

        def _prev():
            self._selected_index -= 1
            self._selected_choice = self._cached_choices[self._selected_index % self.choice_count]

        _prev()
        while self._selected_choice.is_disabled:
            _prev()

    def preferred_width(self, max_available_width: int) -> int:
        max_elem_width = max(list(map(lambda x: x.display_length, self._choices)))
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
            get_line=self._get_line_tokens,
            line_count=self.choice_count,
        )

    @property
    def choice_count(self):
        return len(self._get_available_choices())

    def _get_line_tokens(self, line_number):
        # TODO - gbataille: scope it in the create_content method?
        choice = self._get_available_choices()[line_number]
        tokens = []

        selected = (choice == self.get_selection())

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

    def get_search_string_tokens(self):
        if self._search_string is None:
            return None

        return [
            ('', '\n'),
            ('class:question-mark', '/ '),
            ('class:search', self._search_string),
            ('class:question-mark', '...'),
        ]

    def append_to_search_string(self, char: str) -> None:
        """ Appends a character to the search string """
        if self._search_string is None:
            self._search_string = ''
        self._search_string += char
        self._reset_cached_choices()

    def remove_last_char_from_search_string(self) -> None:
        """ Remove the last character from the search string (~backspace) """
        if self._search_string and len(self._search_string) > 1:
            self._search_string = self._search_string[:-1]
        else:
            self._search_string = None
        self._reset_cached_choices()

    def reset_search_string(self) -> None:
        self._search_string = None


def question(message, choices: List[Choice], default=None, qmark='?', key_bindings=None, **kwargs):
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
                filter=has_search_string & ~IsDone()    # pylint:disable=invalid-unary-operand-type
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
        choices_control.select_next_choice()

    @key_bindings.add(Keys.Up, eager=True)
    def move_cursor_up(_event):        # pylint:disable=unused-variable
        choices_control.select_previous_choice()

    @key_bindings.add(Keys.Enter, eager=True)
    def set_answer(event):        # pylint:disable=unused-variable
        choices_control.answered = True
        choices_control.reset_search_string()
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
