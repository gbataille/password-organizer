from abc import ABC, abstractmethod
from enum import Enum
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from typing import Any, Callable, List, Optional, Tuple

from ..menu import confirmation_menu, list_choice_menu, read_input, read_password
from ..cli_menu.prompts.listmenu import Choice


class RootAction(Enum):
    LIST_PASSWORDS = 'List passwords'
    CREATE_PASSWORD = 'Create a new password'


ROOT_ACTION_MAPPING = {
    RootAction.LIST_PASSWORDS: "_handle_list_password_action",
    RootAction.CREATE_PASSWORD: "_handle_create_password_action",
}
""" Those methods take no parameter """

assert len(ROOT_ACTION_MAPPING.keys()) == len(RootAction)


class PasswordAction(Enum):
    RETRIEVE = 'Retrieve password value'
    UPDATE = 'Update password value'
    DELETE = 'Delete password'


PASSWORD_ACTION_MAPPING = {
    PasswordAction.RETRIEVE: "_handle_retrieve_password",
    PasswordAction.UPDATE: "_handle_update_password",
    PasswordAction.DELETE: "_handle_delete_password",
}
""" Those methods take the password key as first and unique parameter """

assert len(PASSWORD_ACTION_MAPPING.keys()) == len(PasswordAction)

# Mypy does not support recursive types
# https://github.com/python/mypy/issues/731
ListType = Tuple[List[str], Optional[Callable[[], 'ListType']]]  # type:ignore


class Backend(ABC):

    def __init__(self, *args, back: Optional[Callable] = None, **kwargs):  # pylint:disable=unused-argument  # noqa
        """
        Parameters
        ==========
        back: Optional[Callable]
            The method to call when the user choses to go back from the backend menu
            Passing `None` will mean that the backend menu will not display a *BACK* option
        """
        self._back = back

    @abstractmethod
    def initialize(self) -> None:
        """ Perform the backend setup (region, endpoint, credentials, ...) """

    @abstractmethod
    def title(self) -> None:
        """ Outputs to STDOUT a title / description / documentation for the backend chosen """

    @abstractmethod
    def list_password_keys(self) -> ListType:
        """
        Returns the list of password keys available in the backend

        The backend is a key/value store where the key is the password "Name/reference" and the
        value is the password itself

        Returns
        -------
        Tuple[List[str], Optional[Callable[[], ListType]]]:
            - 0: a list of password keys that are available in the backend
            - 1: an optional callable that corresponds to the next page of passwords and that has
              the same type signature as this method
        """

    @abstractmethod
    def retrieve_password(self, key: str) -> str:
        """ Gets the password value for a given password key """

    @abstractmethod
    def create_password(self, password_key: str, password_value: str) -> None:
        """ Create a new password under the given key in the backend """

    @abstractmethod
    def update_password(self, key: str, password_value: str) -> None:
        """ Updates the password under the given key in the backend """

    @abstractmethod
    def delete_password(self, password_key: str) -> None:
        """ Deletes a password from the backend """

    def get_root_menu_actions(self) -> List[Choice[RootAction]]:
        """
        Returns a list of actions to present in a menu for the root menu of the backend

        Override this method if your backend supports more actions that the default ones.
        If you do, remember to override `get_method_for_root_menu_action`
        """
        return [
            Choice(member.value, member) for member in RootAction
        ]

    def get_method_for_root_menu_action(self, menu_action: Any) -> Callable:
        """
        Returns the method to call for the given menu action

        This method goes in pair with `get_root_menu_actions`
        """
        return getattr(self, ROOT_ACTION_MAPPING[menu_action])

    def get_password_menu_actions(self) -> List[Choice[PasswordAction]]:
        """
        Returns a list of actions to present in a menu for the password menu of the backend

        Override this method if your backend supports more actions that the default ones.
        If you do, remember to override `get_method_for_password_menu_action`
        """
        return [
            Choice(member.value, member) for member in PasswordAction
        ]

    def get_method_for_password_menu_action(self, menu_action: Any) -> Callable:
        """
        Returns the method to call for the given menu action

        This method goes in pair with `get_password_menu_actions`
        """
        return getattr(self, PASSWORD_ACTION_MAPPING[menu_action])

    def main_menu(self) -> None:
        """
        Displays the backend main menu

        By default, proposes all the `RootAction` and call their handler

        Parameters
        ==========
        back: Callable
            The function to call when the user choses to go back
            If set to `None` (default) the menu will not display a *BACK* option
        """
        main_menu_choices = self.get_root_menu_actions()
        action: Optional[RootAction] = list_choice_menu(
            main_menu_choices,              # type:ignore  # too complex for mypy
            'What do you want to do?',
            back=self._back,
        )
        if action is None:
            return
        action_method = self.get_method_for_root_menu_action(action)
        action_method()

    def _handle_list_password_action(
        self,
        use_method: Optional[Callable[[], ListType]] = None
    ) -> None:
        if use_method is not None:
            password_keys, next_page_method = use_method()
        else:
            password_keys, next_page_method = self.list_password_keys()

        password_action_choices: List[Choice[str]] = [
            Choice.from_string(key) for key in password_keys
        ]

        NEXT_PAGE_CODE = 'next_page'
        if next_page_method:
            password_action_choices.append(Choice.separator())
            password_action_choices.append(Choice('Next Page', NEXT_PAGE_CODE, None))

        password_key: Optional[str] = list_choice_menu(
            password_action_choices,
            'Which password do you want to work on?',
            back=self.main_menu,
        )
        if password_key is None:
            return

        if password_key == NEXT_PAGE_CODE:
            return self._handle_list_password_action(use_method=next_page_method)

        self.password_menu(password_key)

    def _handle_create_password_action(self) -> None:
        password_key = read_input((
            'Please enter the name (key) under which to store the password:'
        ))
        password_value = read_password((
            'Please enter the value for the password:'
        ))
        self.create_password(password_key, password_value)
        self.password_menu(password_key)

    def password_menu(self, password_key: str) -> None:
        """
        Displays the menu actions for a specific passwor

        By default, proposes all the `PasswordAction` and call their handler
        """
        password_menu_choices = self.get_password_menu_actions()

        password_action: Optional[PasswordAction] = list_choice_menu(
            password_menu_choices,     # type:ignore  # too complex for mypy
            f'What do you want to do with this password ({password_key})?',
            back=self.main_menu
        )
        if password_action is None:
            return

        action_method = self.get_method_for_password_menu_action(password_action)
        action_method(password_key)

    def _handle_retrieve_password(self, password_key: str) -> None:
        confirmation = confirmation_menu((
            f'Are you sure you want to retrieve {password_key}? '
            'Its value will be displayed in clear on the screen'
        ))

        if not confirmation:
            return self.password_menu(password_key)

        password_value = self.retrieve_password(password_key)
        print_formatted_text(
            HTML(f'\n<title>Password {password_key}:</title> {password_value}\n'),
            style=Style.from_dict({
                'title': '#FF9D00 bold',
            }),
        )
        self.main_menu()

    def _handle_update_password(self, password_key: str) -> None:
        new_password_value = read_password((
            'Please enter the new value for the password.\n'
            '  This will overwrite the old password value (which will be lost):'
        ))
        self.update_password(password_key, new_password_value)
        self.password_menu(password_key)

    def _handle_delete_password(self, password_key: str) -> None:
        confirmation = confirmation_menu((
            f'Are you sure you want to delete password {password_key}? '
            'This operation cannot be undone'
        ))

        if not confirmation:
            return self.password_menu(password_key)

        self.delete_password(password_key)
        self.main_menu()
