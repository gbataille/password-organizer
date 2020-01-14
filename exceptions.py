from abc import ABC, abstractmethod
from enum import Enum


class ExitCode(Enum):
    CANNOT_FIND_BACKEND = 100
    MISSING_AUTHENTICATION = 101
    INIT_FAILED = 102


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


class InitializationFailure(InterruptProgramException):
    """ Failure to perform the backend init procedure """

    @property
    def exit_code(self) -> ExitCode:
        return ExitCode.INIT_FAILED

    @property
    def display_message(self) -> str:
        return "Could not complete the backend initialization procedure"
