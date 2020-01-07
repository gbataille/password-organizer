import boto3
from typing import List

from exceptions import MissingAuthentication
from . import Backend


class AWSSSMBackend(Backend):
    """ Uses AWS SSM Parameter Store as a backend to store passwords """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region = 'us-east-1'

        self.ssm_cli = boto3.client('ssm', region_name=self.region)

        if self.ssm_cli._request_signer._credentials is None:
            # Note that this uses botocore internals. Might change.
            # TODO - gbataille: test this behavior for changes
            raise MissingAuthentication("Could not find any AWS credentials")

    def title(self) -> None:
        print(f"""
AWS SSM Parameter Store backend

Passwords are stored in SSM, in region {self.region}, as encrypted string parameter (SecureString),
using default KMS encryption keys
""")

    def list_password_keys(self) -> List[str]:
        resp = self.ssm_cli.describe_parameters()
        passwords = []
        for param in resp.get('Parameters', []):
            passwords.append(param.get('Name'))
        return passwords

    def retrieve_password(self, key: str) -> str:
        resp = self.ssm_cli.get_parameter(Name=key, WithDecryption=True)
        return resp.get('Parameter', {}).get('Value')

    def store_password(self, password: str, key: str) -> None:
        raise NotImplementedError("not yet done")
