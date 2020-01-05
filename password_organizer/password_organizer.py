from enum import Enum
from pprint import pprint
from PyInquirer import prompt
from pyfiglet import Figlet

from .backends import AWSSSMBackend


class Action(Enum):
    LIST_PASSWORDS = 'List passwords'


def main():
    figlet = Figlet(font='slant', width=150)
    print(figlet.renderText("Password Organizer"))
    print('\n\n\n')
    print('Using backend: AWS SSM Parameter Store\n')
    backend = AWSSSMBackend()
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'What do you want to do?',
            'choices': [
                {'name': member.value, 'value': member} for member in Action
            ],
            'default': 0,
        }
    ]

    answers = prompt(questions)
    if answers['action'] == Action.LIST_PASSWORDS:
        pprint(backend.list_passwords())

    return 42
