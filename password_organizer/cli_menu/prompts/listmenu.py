from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import Condition, IsDone
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.dimension import LayoutDimension as D
import string

from ..separator import Separator
from .common import default_style


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, **kwargs):
        self.selected_option_index = 0
        self.answered = False
        self.choices = choices
        self._init_choices(choices, kwargs.pop('default'))
        self.search_string = None
        super(InquirerControl, self).__init__(
            text=self._get_choice_tokens,
            **kwargs
        )

    def _init_choices(self, choices, default=None):
        # helper to convert from question format to internal format
        self.choices = []  # list (name, value, disabled)
        self.selected_option_index = -1
        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append((c, None, None))
            else:
                if isinstance(c, str):
                    self.choices.append((c, c, None))
                    if self.selected_option_index == -1:
                        self.selected_option_index = i
                else:
                    name = c.get('name')
                    value = c.get('value', name)
                    disabled = c.get('disabled', None)
                    self.choices.append((name, value, disabled))
                    if value == default:
                        self.selected_option_index = i

                    if self.selected_option_index == -1 and not disabled:
                        self.selected_option_index = i  # found the first choice

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens = []

        def append(index, choice):
            if self.search_string:
                if (
                    isinstance(choice[0], Separator)
                    or (
                        isinstance(choice[0], str)
                        and not choice[0].startswith(self.search_string)
                    )
                ):
                    if index == self.selected_option_index:
                        # the current selection is masked, moving to the next visible entry
                        # FIXME: when no choices left to display, selection is out of bound
                        self.selected_option_index += 1
                    return

            selected = (index == self.selected_option_index)

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
            tokens.append(('', '\n'))

        # prepare the select choices
        for i, choice in enumerate(self.choices):
            append(i, choice)
        if tokens:
            tokens.pop()  # Remove last newline if any
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


def question(message, **kwargs):
    if 'choices' not in kwargs:
        raise ValueError('You must provide a choices parameter')

    choices = kwargs.pop('choices', None)
    default = kwargs.pop('default', 0)
    qmark = kwargs.pop('qmark', '?')
    kb = kwargs.pop('keybindings', KeyBindings())

    ic = InquirerControl(
        choices,
        default=default
    )

    def get_prompt_tokens():
        tokens = []

        tokens.append(('class:question-mark', qmark))
        tokens.append(('class:question', ' %s ' % message))
        if ic.answered:
            tokens.append(('class:answer', ' ' + ic.get_selection()[0]))
        else:
            tokens.append(('class:instruction', ' (Use arrow keys)'))
        return tokens

    @Condition
    def has_search_string():
        return ic.get_search_string_tokens is not None

    # assemble layout
    layout = Layout(
        HSplit([
            Window(
                height=D.exact(1),
                content=FormattedTextControl(get_prompt_tokens)
            ),
            ConditionalContainer(
                Window(ic),
                filter=~IsDone()        # pylint:disable=invalid-unary-operand-type
            ),
            ConditionalContainer(
                Window(
                    height=D.exact(2),
                    content=FormattedTextControl(ic.get_search_string_tokens)
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
            ic.selected_option_index = (
                (ic.selected_option_index + 1) % ic.choice_count)
        _next()
        while isinstance(ic.choices[ic.selected_option_index][0], Separator) or\
                ic.choices[ic.selected_option_index][2]:
            _next()

    @kb.add(Keys.Up, eager=True)
    def move_cursor_up(_event):        # pylint:disable=unused-variable
        def _prev():
            ic.selected_option_index = (
                (ic.selected_option_index - 1) % ic.choice_count)
        _prev()
        while isinstance(ic.choices[ic.selected_option_index][0], Separator) or \
                ic.choices[ic.selected_option_index][2]:
            _prev()

    @kb.add(Keys.Enter, eager=True)
    def set_answer(event):        # pylint:disable=unused-variable
        ic.answered = True
        ic.search_string = None
        event.app.exit(result=ic.get_selection()[1])

    def search_filter(event):
        if ic.search_string is None:
            ic.search_string = event.key_sequence[0].key
        else:
            ic.search_string += event.key_sequence[0].key

    for character in string.printable:
        kb.add(character, eager=True)(search_filter)

    @kb.add(Keys.Backspace, eager=True)
    def delete_from_search_filter(_event):        # pylint:disable=unused-variable
        if len(ic.search_string) == 1:
            ic.search_string = None
        else:
            ic.search_string = ic.search_string[:-1]

    return Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
        style=default_style,
    )
