from abc import ABC, abstractmethod
from enum import Enum
from PyInquirer import prompt, Separator
from typing import List


BACK = 'Back...'


class RootAction(Enum):
    LIST_PASSWORDS = 'List passwords'


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
        if answers['action'] == RootAction.LIST_PASSWORDS:
            self._handle_list_password_action()

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
            print(answers['password_key'])
