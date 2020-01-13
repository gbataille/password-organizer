import boto3
import json
from typing import List

from .base_aws_backend import BaseAWSBackend


class AWSSecretsManagerBackend(BaseAWSBackend):
    """ Uses AWS SSM Parameter Store as a backend to store passwords """

    def __init__(self, *args, **kwargs):
        # TODO - gbataille: support secrets description
        # TODO - gbataille: support secrets tagging
        super().__init__(*args, **kwargs)
        self.secrets_cli = boto3.client('secretsmanager', region_name=self.region)

    def backend_description(self) -> str:
        return f"""
AWS Secrets Manager backend

Passwords are stored in Secrets Manager, in region {self.region}
Only simple string password are supported so far
"""

    def list_password_keys(self) -> List[str]:
        resp = self.secrets_cli.list_secrets()
        passwords = []
        for param in resp.get('SecretList', []):
            passwords.append(param.get('Name'))
        return passwords

    def retrieve_password(self, key: str) -> str:
        resp = self.secrets_cli.get_secret_value(SecretId=key)
        secret_json = resp.get('SecretString')
        return json.loads(secret_json).get(key)

    def create_password(self, password_key: str, password_value: str) -> None:
        self.secrets_cli.create_secret(
            Name=password_key,
            SecretString=json.dumps({password_key: password_value})
        )

    def update_password(self, key: str, password_value: str) -> None:
        self.secrets_cli.update_secret(
            SecretId=key,
            SecretString=json.dumps({key: password_value})
        )

    def delete_password(self, password_key: str) -> None:
        self.secrets_cli.delete_secret(SecretId=password_key)
