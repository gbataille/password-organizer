from abc import ABC, abstractmethod
from typing import List


class MissingAuthentication(Exception):
    """ Failure to initialize a backend due to missing credentials """
    EXIT_CODE = 100


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
