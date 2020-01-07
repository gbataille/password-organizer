from enum import Enum
from PyInquirer import prompt, Separator
from pyfiglet import Figlet

from .backends import AWSSSMBackend, MissingAuthentication


BACK = 'Back...'


class Action(Enum):
    LIST_PASSWORDS = 'List passwords'


def title():
    figlet = Figlet(font='slant', width=150)
    print(figlet.renderText("Password Organizer"))
    print('\n\n\n')


def main():
    title()

    try:
        backend = AWSSSMBackend()
    except MissingAuthentication as e:
        print(f"Error: {str(e)}")
        return e.EXIT_CODE

    backend.title()

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
        password_keys = backend.list_password_keys()

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
        return main()
    else:
        print(answers['password_key'])

    return 0
