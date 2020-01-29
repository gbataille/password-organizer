# Password Organizer

![](https://github.com/gbataille/password-organizer/workflows/tox-build/badge.svg)
![](https://codecov.io/github/gbataille/password-organizer/coverage.svg)

## What is it?

`password-organizer` is a **CLI** interactive **menu** to browse your password vault(s).

It is not a password vault itself, and relies on thirdparty backends like AWS SSM or HashiCorp
Vault. See [Backends](#backends) for more details about what is currently supported.

[![asciicast](https://asciinema.org/a/AyujEPdjcDmSPoOK26pTozCiO.svg)](https://asciinema.org/a/AyujEPdjcDmSPoOK26pTozCiO)

## Backends

* [AWS SSM Parameter Store](./docs/backends/AWS_SSM.md)
* [AWS Secrets Manager](./docs/backends/AWS_SecretsManager.md)

## Troubleshooting

[Troubleshooting](./docs/TROUBLESHOOTING.md)

## Contributing

Contribution are welcome. You can look up the [following instructions](./docs/CONTRIBUTING.md)

## Links

[Code Coverage](https://codecov.io/gh/gbataille/password-organizer)
