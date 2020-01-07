from abc import ABC, abstractmethod
from enum import Enum


class ExitCode(Enum):
    MISSING_AUTHENTICATION = 100


class InterruptProgramException(Exception, ABC):
    """ Exceptions that should interrupt the program with a particular message and code """

    @property
    @abstractmethod
    def exit_code(self) -> ExitCode:
        """ The unix exit code to use. See ExitCode """

    @property
    @abstractmethod
    def display_message(self) -> str:
        """ The message to be displayed to the user """


class MissingAuthentication(InterruptProgramException):
    """ Failure to initialize a backend due to missing credentials """

    @property
    def exit_code(self) -> ExitCode:
        return ExitCode.MISSING_AUTHENTICATION

    @property
    def display_message(self) -> str:
        return "Could not find any credentials"
