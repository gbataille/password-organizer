from enum import Enum
from pyfiglet import Figlet

from exceptions import InterruptProgramException
from .backends import AWSSSMBackend


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
    except InterruptProgramException as e:
        print(f"Error: \n\t{e.display_message}")
        return e.exit_code.value

    backend.title()
    return backend.run()
