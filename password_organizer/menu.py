from copy import deepcopy
from typing import Dict, List, Optional, TypeVar, Union

from .cli_menu import prompt, Separator


class UserExit(Exception):
    """ Exception representing the user wanting to quit the program """


T = TypeVar('T')
Choice = Union[T, Dict[str, T], Separator, str]

QUIT = 'Exit (Ctrl+c)'


def list_choice_menu(
    choices: List[Choice],
    message: str,
    default: Optional[Union[int, T]] = None,
    quit_option_text: Optional[str] = QUIT,
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

    Returns
    -------
    T
        The choice that the user made

    Raises
    ------
    UserExit
        When the user chose the "Quit" alternative
    """
    menu_choices = deepcopy(choices)
    if quit_option_text:
        menu_choices.extend([Separator(), quit_option_text])
    questions = [
        {
            'type': 'listmenu',
            'name': 'action',
            'message': message,
            'choices': menu_choices,
            'default': default,
        }
    ]

    answers = prompt(questions)
    action = answers['action']
    if action == quit_option_text:
        raise UserExit()
    else:
        return action
