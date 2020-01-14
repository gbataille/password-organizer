from copy import deepcopy
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import confirm
from typing import Callable, List, Optional, TypeVar, Union

from .cli_menu import prompt
from .cli_menu.prompts.listmenu import Choice


class UserExit(Exception):
    """ Exception representing the user wanting to quit the program """


T = TypeVar('T')

BACK = 'Back...'
QUIT = 'Exit'


def confirmation_menu(message: str) -> bool:
    return confirm(message=message)


def read_input(message: str) -> str:
    questions = [
        {
            'type': 'std_input',
            'name': 'value',
            'message': message,
        }
    ]
    answers = prompt(questions)
    return answers['value']


def read_password(message: str) -> str:
    questions = [
        {
            'type': 'password',
            'name': 'password_value',
            'message': message,
        }
    ]
    answers = prompt(questions)
    return answers['password_value']


def list_choice_menu(
    choices: List[Choice[T]],
    message: str,
    default: Optional[Union[int, T]] = None,
    back: Optional[Callable] = None,
    quit_option_text: Optional[str] = QUIT,
    use_ctrl_c_to_quit: bool = True,
) -> Optional[T]:
    """
    Displays a list menu

    Parameters
    ----------
    choices: List[ChoiceT]
        A list of `ChoiceT` that the user can chose from in the menu
    message: str
        The question to be displayed at the top of the choice menu
    default: Optional[Union[int, T]]
        The default answer
    back: Optional[Callable[]]
        The function to call if the user choses to go back
        Leave blank if you don't want a "BACK" option
    quit_option_text: Optional[str]
        The text to display for the bottom "QUIT" option
        If you don't want a "QUIT" option, set this parameter to None
    use_ctrl_c_to_quit: bool
        Whether or not Ctrl C is intercepted to quit the menu
        When it is, the information is appended to the `quit_option_text`
        Defaults to True

    Returns
    -------
    Optional[T]
        - The choice that the user made
        - None if he chose to go back

    Raises
    ------
    UserExit
        When the user chose the "Quit" alternative
    """
    if use_ctrl_c_to_quit:
        kb = KeyBindings()

        def quit_menu(event):
            event.app.exit(exception=UserExit())

        kb.add(Keys.ControlC, eager=True)(quit_menu)

        if quit_option_text:
            quit_option_text += ' (Ctrl+c)'

    menu_choices = deepcopy(choices)
    if back:
        menu_choices.extend([Choice.separator(), Choice.from_string(BACK)])
    if quit_option_text:
        menu_choices.extend([Choice.separator(), Choice.from_string(quit_option_text)])

    question_args = {
        'type': 'listmenu',
        'name': 'action',
        'message': message,
        'choices': menu_choices,
        'default': default,
    }
    if use_ctrl_c_to_quit:
        question_args['key_bindings'] = kb

    questions = [question_args]
    answers = prompt(questions)
    action = answers['action']
    if action == quit_option_text:
        raise UserExit()
    if action == BACK:
        back()    # type:ignore  # mypy can't see that action can't be BACK if back is NONE
        return None
    else:
        return action
