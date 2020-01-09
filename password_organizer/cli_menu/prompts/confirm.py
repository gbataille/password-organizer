"""
confirm type question
"""
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.styles import Style


default_style = Style.from_dict({
    'set-cursor-position':  '#FF9D00 bold',
    'separator': '#6C6C6C',
    'question-mark': 'noinherit #5F819D bold',
    'selected': 'noinherit #5F819D bold',
    'pointer': '#FF9D00 bold',
    'instruction': '',
    'answer': '#FF9D00 bold',
    'question': 'bold',
})


def question(message, **kwargs):
    default = kwargs.pop('default', True)

    status = {'answer': None}

    qmark = kwargs.pop('qmark', '?')

    def get_prompt_tokens():
        tokens = []

        tokens.append(('class:question-mark', qmark))
        tokens.append(('class:question', ' %s ' % message))
        if isinstance(status['answer'], bool):
            tokens.append(('class:answer', ' Yes' if status['answer'] else ' No'))
        else:
            if default:
                instruction = ' (Y/n)'
            else:
                instruction = ' (y/N)'
            tokens.append(('class:instruction', instruction))
        return tokens

    # key bindings
    kb = KeyBindings()

    @kb.add(Keys.ControlQ, eager=True)
    @kb.add(Keys.ControlC, eager=True)
    def _(event):
        raise KeyboardInterrupt()

    @kb.add('n')
    @kb.add('N')
    def key_n(event):       # pylint:disable=unused-variable
        status['answer'] = False
        event.app.exit(result=False)

    @kb.add('y')
    @kb.add('Y')
    def key_y(event):       # pylint:disable=unused-variable
        status['answer'] = True
        event.app.exit(result=True)

    @kb.add(Keys.Enter, eager=True)
    def set_answer(event):      # pylint:disable=unused-variable
        status['answer'] = default
        event.app.exit(result=default)

    # assemble layout
    layout = Layout(
        HSplit([
            Window(
                height=D.exact(1),
                content=FormattedTextControl(get_prompt_tokens)
            ),
        ])
    )

    return Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=False,
        style=default_style,
    )
