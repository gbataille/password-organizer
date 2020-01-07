from enum import Enum
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
    return backend.run()
