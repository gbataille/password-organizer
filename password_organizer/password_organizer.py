import importlib
from pyfiglet import Figlet

from exceptions import InterruptProgramException, ExitCode
from .menu import list_choice_menu, UserExit


BACKENDS = {
    "AWS SSM Parameter Store": ("password_organizer.backends", "AWSSSMBackend"),
    "AWS Secrets Manager": ("password_organizer.backends", "AWSSecretsManagerBackend"),
}


def app_title():
    figlet = Figlet(font='slant', width=150)
    print(figlet.renderText("Password Organizer"))
    print('\n')


def main() -> int:
    app_title()
    return backend_menu()


def backend_menu() -> int:
    try:
        backend_key = list_choice_menu(
            list(BACKENDS.keys()),
            "Which backend do you want to use?"
        )
        if backend_key is None:
            # There is no "back" option in the menu above, so this code path should not be possible
            print("No choice, leaving...")
            return 0
    except UserExit:
        print("\nGoodbye\n")
        return 0

    backend_module, backend_class = BACKENDS[backend_key]

    try:
        module = importlib.import_module(backend_module)
        clazz = getattr(module, backend_class)
    except Exception as e:
        print(f"Error: \n\t{str(e)}")
        return ExitCode.CANNOT_FIND_BACKEND.value

    try:
        backend = clazz(back=backend_menu)
    except InterruptProgramException as e:
        print(f"Error: \n\t{e.display_message}")
        return e.exit_code.value

    try:
        backend.initialize()
        backend.title()
        return backend.main_menu()
    except UserExit:
        print("\nGoodbye\n")
        return 0
