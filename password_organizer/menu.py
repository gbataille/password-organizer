from copy import deepcopy
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from typing import Dict, List, Optional, TypeVar, Union

from .cli_menu import prompt, Separator


class UserExit(Exception):
    """ Exception representing the user wanting to quit the program """


T = TypeVar('T')
Choice = Union[T, Dict[str, T], Separator, str]

QUIT = 'Exit'


def list_choice_menu(
    choices: List[Choice],
    message: str,
    default: Optional[Union[int, T]] = None,
    quit_option_text: Optional[str] = QUIT,
    use_ctrl_c_to_quit: bool = True,
) -> T:
    """
    Displays a list menu

    Parameters
    ----------
    choices: List[Choice]
        A list of `Choice` that the user can chose from in the menu
    message: str
        The question to be displayed at the top of the choice menu
    default: Optional[Union[int, T]]
        The default answer
    quit_option_text: Optional[str]
        The text to display for the bottom "QUIT" option
        If you don't want a "QUIT" option, set this parameter to None
    use_ctrl_c_to_quit: bool
        Whether or not Ctrl C is intercepted to quit the menu
        When it is, the information is appended to the `quit_option_text`
        Defaults to True

    Returns
    -------
    T
        The choice that the user made

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
    if quit_option_text:
        menu_choices.extend([Separator(), quit_option_text])

    question_args = {
        'type': 'listmenu',
        'name': 'action',
        'message': message,
        'choices': menu_choices,
        'default': default,
    }
    if use_ctrl_c_to_quit:
        question_args['keybindings'] = kb

    questions = [question_args]
    answers = prompt(questions)
    action = answers['action']
    if action == quit_option_text:
        raise UserExit()
    else:
        return action
