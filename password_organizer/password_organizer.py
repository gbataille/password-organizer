from pyfiglet import Figlet

from exceptions import InterruptProgramException
from .backends import AWSSSMBackend, AWSSecretsManagerBackend


def title():
    figlet = Figlet(font='slant', width=150)
    print(figlet.renderText("Password Organizer"))
    print('\n')


def main():
    # TODO - gbataille: choose backend
    # TODO - gbataille: for AWS backend, chose region
    # TODO - gbataille: for AWS backend, display on which account it is connected
    title()

    try:
        # backend = AWSSSMBackend()
        backend = AWSSecretsManagerBackend()
    except InterruptProgramException as e:
        print(f"Error: \n\t{e.display_message}")
        return e.exit_code.value

    backend.title()
    return backend.main_menu()
