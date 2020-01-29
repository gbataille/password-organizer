# Contributing

## Setting up a dev environment

This is a classic python project. You can therefore simply create a virtual environment in your
prefered manner, then

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_test.txt
```

## Building the code

This project uses `tox` to perform linting, pep8 checking, type hint checking and running tests

```bash
tox
```

## Running the program locally

The main module is called `password_organizer`. And the binary entrypoint lives in
`bin/passsword-organizer`

So you can do either

```bash
python -m password_organizer
```

or

```bash
./bin/password_organizer
```

## Adding a new backend

Backends need to extend `password_organizer.backends.base.Backend` and implement its abstract
methods. At minimum, a backend needs to be able to:
- List the password it contains
- Create a new password (key/value pair)
- Retrieve an existing password
- Updating an existing password's value
- Deleting a password

### Example

The [password_organizer.backends.AWSSSMBackend](../password_organizer/backends/aws_ssm_backend.py)
is the backend with the most features and is a good place to find inspiration

### Custom initialization

If your backend need to interact with the user to initialize itself, you can do that through the
`initialize` method that will be called after the backend is instantiated.

For example, the AWS backends will ask the user in which region he wants to work at that point.

### Adding actions

Each menu / actions can be customized. Entries in menus can be added by overriding methods such as
`Backend.get_root_menu_actions`. Consult the documentation of the `Backend` class to see what can be
done.
