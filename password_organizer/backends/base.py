from abc import ABC, abstractmethod
from enum import Enum
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from typing import Any, List

from ..cli_menu import prompt, Separator


BACK = 'Back...'


class RootAction(Enum):
    LIST_PASSWORDS = 'List passwords'


ROOT_ACTION_MAPPING = {
    RootAction.LIST_PASSWORDS: "_handle_list_password_action"
}
""" Those methods take no parameter """

assert len(ROOT_ACTION_MAPPING.keys()) == len(RootAction)


class PasswordAction(Enum):
    RETRIEVE = 'Retrieve password value'
    UPDATE = 'Update password value'


PASSWORD_ACTION_MAPPING = {
    PasswordAction.RETRIEVE: "_handle_retrieve_password",
    PasswordAction.UPDATE: "_handle_update_password",
}
""" Those methods take the password key as first and unique parameter """

assert len(PASSWORD_ACTION_MAPPING.keys()) == len(PasswordAction)


class Backend(ABC):

    @abstractmethod
    def title(self) -> None:
        """ Outputs to STDOUT a title / description / documentation for the backend chosen """

    @abstractmethod
    def list_password_keys(self) -> List[str]:
        """
        Returns the list of password keys available in the backend

        The backend is a key/value store where the key is the password "Name/reference" and the
        value is the password itself
        """

    @abstractmethod
    def retrieve_password(self, key: str) -> str:
        """ Gets the password value for a given password key """

    # TODO - gbataille: separate create and update
    @abstractmethod
    def store_password(self, key: str, password_value: str) -> None:
        """ Stores the password under the given key in the backend """

    # TODO - gbataille:
    # @abstractmethod
    # def delete_password(self, password_key: str) -> None:
    #     """ Deletes a password from the backend """

    def main_menu(self) -> None:
        """
        Displays the backend main menu

        By default, proposes all the `RootAction` and call their handler
        """
        questions = [
            {
                'type': 'listmenu',
                'name': 'action',
                'message': 'What do you want to do?',
                'choices': [
                    {'name': member.value, 'value': member} for member in RootAction
                ],
                'default': 0,
            }
        ]

        try:
            answers = prompt(questions)
            action = answers['action']
            action_method = getattr(self, ROOT_ACTION_MAPPING[action])
            action_method()
        except KeyboardInterrupt:
            print("\nInterrupted\nGoodbye\n")

    def _handle_list_password_action(self) -> None:
        password_keys = self.list_password_keys()

        password_action_choices: List[Any] = password_keys
        password_action_choices.extend([Separator(), BACK])
        questions = [
            {
                'type': 'listmenu',
                'name': 'password_key',
                'message': 'Which password do you want to work on?',
                'choices': password_action_choices,
            }
        ]
        answers = prompt(questions)
        password_key = answers['password_key']
        if password_key == BACK:
            print('\n')
            self.main_menu()
        else:
            self.password_menu(password_key)

    def password_menu(self, password_key: str) -> None:
        """
        Displays the menu actions for a specific passwor

        By default, proposes all the `PasswordAction` and call their handler
        """
        password_menu_choices: List[Any] = [
            {'name': member.value, 'value': member} for member in PasswordAction
        ]
        password_menu_choices.extend([Separator(), {'name': BACK, 'value': BACK}])

        questions = [
            {
                'type': 'listmenu',
                'name': 'password_action',
                'message': f'What do you want to do with this password ({password_key})?',
                'choices': password_menu_choices,
            }
        ]
        answers = prompt(questions)
        password_action = answers['password_action']
        if password_action == BACK:
            print('\n')
            self.main_menu()
        else:
            action_method = getattr(self, PASSWORD_ACTION_MAPPING[password_action])
            action_method(password_key)

    def _handle_retrieve_password(self, password_key: str) -> None:
        questions = [
            {
                'type': 'confirm',
                'name': 'confirmation',
                'message': (
                    f'Are you sure you want to retrieve {password_key}? '
                    'Its value will be displayed in clear on the screen'
                ),
            }
        ]
        answers = prompt(questions)
        confirmation = answers['confirmation']
        if not confirmation:
            self.password_menu(password_key)

        password_value = self.retrieve_password(password_key)
        print_formatted_text(
            HTML(f'\n<title>Password {password_key}:</title> {password_value}\n'),
            style=Style.from_dict({
                'title': '#FF9D00 bold',
            }),
        )
        self.main_menu()

    def _handle_update_password(self, password_key: str) -> None:
        questions = [
            {
                'type': 'password',
                'name': 'new_password_value',
                'message': (
                    'Please enter the new value for the password.\n'
                    '  This will overwrite the old password value (which will be lost):'
                ),
                'multiline': True,
            }
        ]
        answers = prompt(questions)
        new_password_value = answers['new_password_value']
        self.store_password(password_key, new_password_value)
        self.password_menu(password_key)
