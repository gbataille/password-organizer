import importlib
from pyfiglet import Figlet

from exceptions import InterruptProgramException, ExitCode
from .menu import list_choice_menu


BACKENDS = {
    "AWS SSM Parameter Store": ("password_organizer.backends", "AWSSSMBackend"),
    "AWS Secrets Manager": ("password_organizer.backends", "AWSSecretsManagerBackend"),
}


def app_title():
    figlet = Figlet(font='slant', width=150)
    print(figlet.renderText("Password Organizer"))
    print('\n')


def main() -> int:
    # TODO - gbataille: choose backend
    # TODO - gbataille: for AWS backend, chose region
    # TODO - gbataille: for AWS backend, display on which account it is connected
    app_title()
    return backend_menu()


def backend_menu() -> int:
    backend_key = list_choice_menu(
        list(BACKENDS.keys()),
        "Which backend do you want to use?"
    )
    if backend_key is None:
        # There is no "back" option in the menu above, so this code path should not be possible
        print("No choice, leaving...")
        return 0

    backend_module, backend_class = BACKENDS[backend_key]

    try:
        module = importlib.import_module(backend_module)
        clazz = getattr(module, backend_class)
    except Exception as e:
        print(f"Error: \n\t{str(e)}")
        return ExitCode.CANNOT_FIND_BACKEND.value

    try:
        backend = clazz()
    except InterruptProgramException as e:
        print(f"Error: \n\t{e.display_message}")
        return e.exit_code.value

    backend.title()
    return backend.main_menu(back=backend_menu)
