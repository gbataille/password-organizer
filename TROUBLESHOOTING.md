# Troubleshooting

## AWS Backends

### Common

#### Getting an error on the account ID retrieval

Getting the client ID requires that your connection has the `sts:GetCallerIdentity` action. To test
if you have it, you can run the following command (assuming you have `awscli` installed), with the
same credentials you use with `password-organizer`:

```bash
aws sts get-caller-identity
```

#### Getting an error on the account alias retrieval

Getting the client ID requires that your connection has the `iam:ListAccountAliases` action. To test
if you have it, you can run the following command (assuming you have `awscli` installed), with the
same credentials you use with `password-organizer`:

```bash
aws iam list-account-aliases
```

### AWS SSM Parameter Store

#### Getting Access Denied errors

To interact with the AWS SSM Parameter Store, you'll need the following actions:
- `ssm:PutParameter`
- `ssm:DeleteParameter`
- `ssm:GetParameter`
- `ssm:DescribeParameters`

### AWS Secrets Manager

#### Getting Access Denied errors

To interact with the AWS Secrets Manager, you'll need the following actions:
- `secretsmanager:ListSecrets`
- `secretsmanager:CreateSecret`
- `secretsmanager:GetSecretValue`
- `secretsmanager:UpdateSecret`
- `secretsmanager:DeleteSecret`
