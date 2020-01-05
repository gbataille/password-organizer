from abc import ABC, abstractmethod
from typing import List


class Backend(ABC):

    @abstractmethod
    def list_passwords(self) -> List[str]:
        """ Returns the list of passwords available in the backend """

    @abstractmethod
    def retrieve_password(self, key: str) -> str:
        """ Gets the password value for a given password key """

    @abstractmethod
    def store_password(self, password: str, key: str) -> None:
        """ Stores the password under the given key in the backend """
