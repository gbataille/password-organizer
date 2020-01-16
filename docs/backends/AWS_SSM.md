# AWS SSM Parameter Store

This backend uses the SSM Parameter Store of AWS to store passwords.

Password are stored using the `SecureString` type, which encrypting the password value with the
default KMS key.

## AWS Documentation

https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
