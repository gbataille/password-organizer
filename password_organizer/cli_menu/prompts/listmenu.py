from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import IsDone
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.dimension import LayoutDimension as D

from ..separator import Separator
from .common import default_style


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, **kwargs):
        self.selected_option_index = 0
        self.answered = False
        self.choices = choices
        self._init_choices(choices, kwargs.pop('default'))
        super(InquirerControl, self).__init__(self._get_choice_tokens, **kwargs)

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
        tokens.pop()  # Remove last newline.
        return tokens

    def get_selection(self):
        return self.choices[self.selected_option_index]


def question(message, **kwargs):
    if 'choices' not in kwargs:
        raise ValueError('You must provide a choices parameter')

    choices = kwargs.pop('choices', None)
    default = kwargs.pop('default', 0)
    qmark = kwargs.pop('qmark', '?')
    kb = kwargs.pop('keybindings', KeyBindings())

    ic = InquirerControl(choices, default=default)

    def get_prompt_tokens():
        tokens = []

        tokens.append(('class:question-mark', qmark))
        tokens.append(('class:question', ' %s ' % message))
        if ic.answered:
            tokens.append(('class:answer', ' ' + ic.get_selection()[0]))
        else:
            tokens.append(('class:instruction', ' (Use arrow keys)'))
        return tokens

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
            )
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
        event.app.exit(result=ic.get_selection()[1])

    return Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
        style=default_style,
    )
