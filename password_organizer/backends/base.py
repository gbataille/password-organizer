from abc import ABC, abstractmethod
from enum import Enum
from PyInquirer import prompt, Separator
from typing import List


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


PASSWORD_ACTION_MAPPING = {
    PasswordAction.RETRIEVE: "_handle_retrieve_password"
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

    @abstractmethod
    def store_password(self, password: str, key: str) -> None:
        """ Stores the password under the given key in the backend """

    def main_menu(self) -> None:
        """
        Displays the backend main menu

        By default, proposes all the `RootAction` and call their handler
        """
        questions = [
            {
                'type': 'list',
                'name': 'action',
                'message': 'What do you want to do?',
                'choices': [
                    {'name': member.value, 'value': member} for member in RootAction
                ],
                'default': 0,
            }
        ]

        answers = prompt(questions)
        action = answers['action']
        action_method = getattr(self, ROOT_ACTION_MAPPING[action])
        action_method()

    def _handle_list_password_action(self) -> None:
        password_keys = self.list_password_keys()

        questions = [
            {
                'type': 'list',
                'name': 'password_key',
                'message': 'Which password do you want to work on?',
                'choices': password_keys + [Separator(), BACK],
            }
        ]
        answers = prompt(questions)
        password_key = answers['password_key']
        if password_key == BACK:
            self.main_menu()
        else:
            self.password_menu(password_key)

    def password_menu(self, password_key: str) -> None:
        """
        Displays the menu actions for a specific passwor

        By default, proposes all the `PasswordAction` and call their handler
        """
        questions = [
            {
                'type': 'list',
                'name': 'password_action',
                'message': f'What do you want to do with this password ({password_key})?',
                'choices': [
                    {'name': member.value, 'value': member} for member in PasswordAction
                ] + [Separator(), {'name': BACK, 'value': BACK}],
            }
        ]
        answers = prompt(questions)
        password_action = answers['password_action']
        if password_action == BACK:
            self.main_menu()
        else:
            action_method = getattr(self, PASSWORD_ACTION_MAPPING[password_action])
            action_method(password_key)

    def _handle_retrieve_password(self, password_key: str) -> None:
        password_value = self.retrieve_password(password_key)
        print(f'\nPassword {password_key}: {password_value}\n')
