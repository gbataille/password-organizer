from pyfiglet import Figlet

from exceptions import InterruptProgramException
from .backends import AWSSSMBackend


def title():
    figlet = Figlet(font='slant', width=150)
    print(figlet.renderText("Password Organizer"))
    print('\n')


def main():
    title()

    try:
        backend = AWSSSMBackend()
    except InterruptProgramException as e:
        print(f"Error: \n\t{e.display_message}")
        return e.exit_code.value

    backend.title()
    return backend.main_menu()
