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
