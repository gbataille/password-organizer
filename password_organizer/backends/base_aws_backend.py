from abc import abstractmethod
import boto3

from aws_constants import AWS_REGIONS
from exceptions import InitializationFailure, MissingAuthentication
from . import Backend
from ..menu import list_choice_menu


class BaseAWSBackend(Backend):      # pylint:disable=abstract-method
    """
    Uses some AWS service as a backend to store passwords

    On startup:
    - test that AWS credentials can be found to establish a connection
    - tries to fetch and display the account id and the account alias of the AWS account the user is
      connected to

    Raises
    ======
    MissingAuthentication
        when AWS credentials cannot be found to connect to AWS
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region = 'us-east-1'

        self.sts_cli = boto3.client('sts', region_name=self.region)
        self.iam_cli = boto3.client('iam', region_name=self.region)

        if self.sts_cli._request_signer._credentials is None:
            # Note that this uses botocore internals. Might change.
            # TODO - gbataille: test this behavior for changes
            raise MissingAuthentication()

    def initialize(self) -> None:
        self.region = list_choice_menu(
            AWS_REGIONS,        # type:ignore  # Type too complicated for mypy
            'Which region do you want to work with?',
            0,
            back=self._back,
        )
        if self.region is None:
            raise InitializationFailure()

        self._setup_aws_clients()

    @abstractmethod
    def _setup_aws_clients(self) -> None:
        """
        Used to initialize the AWS client connections.
        Called anytime they need to be refreshed, like when the region changes
        """

    @abstractmethod
    def backend_description(self) -> str:
        """ A description of the AWS based backend, to be displayed at backend initialization """

    def title(self):
        _title = f"Working on AWS, in region {self.region}:\n"

        _title += '- Account ID: '
        try:
            account_id = self.sts_cli.get_caller_identity()['Account']
            # Spaces for manual alignment with account alias
            _title += f'   {account_id}\n'
        except Exception as e:
            _title += f' 💥 Error 💥 - {str(e)[:50]}...\n'

        _title += '- Account alias: '
        try:
            account_aliases = self.iam_cli.list_account_aliases()['AccountAliases']
            if account_aliases:
                _title += f'{account_aliases[0]}\n'
            else:
                _title += 'None\n'
        except Exception as e:
            _title += f' 💥 Error 💥 - {str(e)[:50]}...\n'

        backend_description = self.backend_description()
        print(f"""
===========================================
{_title}
===========================================

{backend_description}
""")
