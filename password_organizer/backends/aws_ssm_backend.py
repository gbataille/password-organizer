import boto3
from typing import List

from . import Backend


class AWSSSMBackend(Backend):
    """ Uses AWS SSM Parameter Store as a backend to store passwords """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ssm_cli = boto3.client('ssm', region_name='us-east-1')

    def list_passwords(self) -> List[str]:
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
