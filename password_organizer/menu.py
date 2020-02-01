from copy import deepcopy
# from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import confirm
import questionary
from questionary.prompt import prompt
from questionary.prompts.common import Choice, Separator
from typing import Any, Callable, List, Optional


class UserExit(Exception):
    """ Exception representing the user wanting to quit the program """


BACK = 'Back...'
QUIT = 'Exit'


def confirmation_menu(message: str) -> bool:
    return confirm(message=message)


def read_input(message: str) -> str:
    return questionary.text(message).ask()


def read_password(message: str) -> str:
    return questionary.password(message).ask()


def list_choice_menu(
    choices: List[Choice],
    message: str,
    default: Optional[Choice] = None,
    back: Optional[Callable] = None,
    quit_option_text: Optional[str] = QUIT,
    # use_ctrl_c_to_quit: bool = True,
) -> Optional[Any]:
    """
    Displays a list menu

    Parameters
    ----------
    choices: List[Choice]
        A list of `Choice` that the user can chose from in the menu
    message: str
        The question to be displayed at the top of the choice menu
    default: Optional[Choice]
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
    Optional
        - The choice that the user made
        - None if he chose to go back

    Raises
    ------
    UserExit
        When the user chose the "Quit" alternative
    """
    # TODO: adapt to questionary
    # if use_ctrl_c_to_quit:
    #     kb = KeyBindings()
    #
    #     def quit_menu(event):
    #         event.app.exit(exception=UserExit())
    #
    #     kb.add(Keys.ControlC, eager=True)(quit_menu)
    #
    #     if quit_option_text:
    #         quit_option_text += ' (Ctrl+c)'

    menu_choices = deepcopy(choices)
    if back:
        menu_choices.extend([Separator(), Choice.build(BACK)])
    if quit_option_text:
        menu_choices.extend([Separator(), Choice.build(quit_option_text)])

    question_args = {
        'type': 'select',
        'name': 'action',
        'message': message,
        'choices': menu_choices,
        'default': default,
    }
    # TODO: adapt to questionary
    # if use_ctrl_c_to_quit:
    #     question_args['key_bindings'] = kb

    questions = [question_args]
    answers = prompt(questions)
    if not answers:
        raise UserExit()

    action = answers['action']
    if action == quit_option_text:
        raise UserExit()
    if action == BACK:
        back()    # type:ignore  # mypy can't see that action can't be BACK if back is NONE
        return None
    else:
        return action
