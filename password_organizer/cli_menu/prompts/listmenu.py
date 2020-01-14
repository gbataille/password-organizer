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
from typing import Optional

from ..separator import Separator
from .common import default_style


class ChoicesControl(UIControl):
    """
    Menu to display some textual choices.
    Provide a search feature by just typing the start of the entry desired
    """
    def __init__(self, choices, **kwargs):
        self.selected_option_index = -1
        self.answered = False
        self.search_string = None
        self.choices = []
        self._init_choices(choices, kwargs.pop('default'))
        super().__init__(**kwargs)

    def _init_choices(self, choices, default=None):
        for i, c in enumerate(choices):
            choice = None
            if isinstance(c, Separator):
                choice = self._separator_to_choice()
            elif isinstance(c, str):
                choice = self._str_to_choice(c)
            else:
                choice = self._dict_to_choice(c)

            self.choices.append(choice)

            if choice[0] == default:
                self.selected_option_index = i

            # First non disabled choice
            if self.selected_option_index == -1 and choice[2] is None:
                self.selected_option_index = i

    def _separator_to_choice(self):
        return (Separator(), None, '')

    def _str_to_choice(self, choice_str):
        return (choice_str, choice_str, None)

    def _dict_to_choice(self, choice_dict):
        return (
            choice_dict.get('name'),
            choice_dict.get('value', choice_dict.get('name')),
            choice_dict.get('disabled', None)
        )

    def preferred_width(self, max_available_width: int) -> int:
        max_elem_width = max(list(map(len, self.choices)))
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
                isinstance(choice[0], Separator)
                or (
                    isinstance(choice[0], str)
                    and not choice[0].startswith(self.search_string)
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

        if choice[2]:  # disabled
            tokens.append(('class:selected' if selected else 'class:disabled',
                           '- %s (%s)' % (choice[0], choice[2])))
        else:
            try:
                tokens.append(('class:selected' if selected else '', str(choice[0])))
            except Exception:
                tokens.append(('class:selected' if selected else '', choice[0]))

        return tokens

    def get_selection(self):
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
        self.search_string = '' if self.search_string is None else self.search_string
        self.search_string += char

    def remove_last_char_from_search_string(self) -> None:
        """ Remove the last character from the search string (~backspace) """
        if self.search_string and len(self.search_string) > 1:
            self.search_string = self.search_string[:-1]
        else:
            self.search_string = None


def question(message, **kwargs):
    if 'choices' not in kwargs:
        raise ValueError('You must provide a choices parameter')

    choices = kwargs.pop('choices', None)
    default = kwargs.pop('default', 0)
    qmark = kwargs.pop('qmark', '?')
    kb = kwargs.pop('keybindings', KeyBindings())

    choices_control = ChoicesControl(
        choices,
        default=default
    )

    def get_prompt_tokens():
        tokens = []

        tokens.append(('class:question-mark', qmark))
        tokens.append(('class:question', ' %s ' % message))
        if choices_control.answered:
            tokens.append(('class:answer', ' ' + choices_control.get_selection()[0]))
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

    @kb.add(Keys.ControlQ, eager=True)
    def exit_menu(event):
        event.app.exit(exception=KeyboardInterrupt())

    if not kb.get_bindings_for_keys((Keys.ControlC,)):
        kb.add(Keys.ControlC, eager=True)(exit_menu)

    @kb.add(Keys.Down, eager=True)
    def move_cursor_down(_event):        # pylint:disable=unused-variable
        def _next():
            choices_control.selected_option_index = (
                (choices_control.selected_option_index + 1) % choices_control.choice_count)
        _next()
        while (
            isinstance(choices_control.choices[choices_control.selected_option_index][0], Separator)
            or choices_control.choices[choices_control.selected_option_index][2]
        ):
            _next()

    @kb.add(Keys.Up, eager=True)
    def move_cursor_up(_event):        # pylint:disable=unused-variable
        def _prev():
            choices_control.selected_option_index = (
                (choices_control.selected_option_index - 1) % choices_control.choice_count)
        _prev()
        while (
            isinstance(choices_control.choices[choices_control.selected_option_index][0], Separator)
            or choices_control.choices[choices_control.selected_option_index][2]
        ):
            _prev()

    @kb.add(Keys.Enter, eager=True)
    def set_answer(event):        # pylint:disable=unused-variable
        choices_control.answered = True
        choices_control.search_string = None
        event.app.exit(result=choices_control.get_selection()[1])

    def search_filter(event):
        choices_control.append_to_search_string(event.key_sequence[0].key)

    for character in string.printable:
        kb.add(character, eager=True)(search_filter)

    @kb.add(Keys.Backspace, eager=True)
    def delete_from_search_filter(_event):        # pylint:disable=unused-variable
        choices_control.remove_last_char_from_search_string()

    return Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
        style=default_style,
    )
