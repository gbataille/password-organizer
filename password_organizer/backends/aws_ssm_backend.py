import boto3
from typing import List

from .base_aws_backend import BaseAWSBackend


class AWSSSMBackend(BaseAWSBackend):
    """ Uses AWS SSM Parameter Store as a backend to store passwords """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssm_cli = None

    def _setup_aws_clients(self) -> None:
        self.ssm_cli = boto3.client('ssm', region_name=self.region)

    def backend_description(self) -> str:
        return f"""
AWS SSM Parameter Store backend

Passwords are stored in SSM, in region {self.region}, as encrypted string parameter (SecureString),
using default KMS encryption keys
"""

    def list_password_keys(self) -> List[str]:
        # FIXME: only gets the first page of passwords!!!
        resp = self.ssm_cli.describe_parameters(
            MaxResults=50
        )
        passwords = []
        for param in resp.get('Parameters', []):
            passwords.append(param.get('Name'))
        passwords.sort()
        return passwords

    def retrieve_password(self, key: str) -> str:
        resp = self.ssm_cli.get_parameter(Name=key, WithDecryption=True)
        return resp.get('Parameter', {}).get('Value')

    def create_password(self, password_key: str, password_value: str) -> None:
        self._write_password(password_key, password_value)

    def update_password(self, key: str, password_value: str) -> None:
        self._write_password(key, password_value)

    def _write_password(self, password_key: str, password_value: str) -> None:
        self.ssm_cli.put_parameter(
            Name=password_key,
            Value=password_value,
            Type='SecureString',
            Overwrite=True,
        )

    def delete_password(self, password_key: str) -> None:
        self.ssm_cli.delete_parameter(Name=password_key)
