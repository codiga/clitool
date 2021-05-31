# Development

## Creating a virtualenv to test

We recommend to use a virtual environment to write code
as it will not use everything from your global python
setup.

To set up a virtual environment:

```shell
python3 -mvenv venv
```

To activate the virtual environment.

```shell
venv/bin/activate
```

To install the dependencies:

```shell
pip install -r requirements.txt
```

### Running tests

To run the tests, just enter the following command.

```shell
PYTHONPATH=. python3 -m unittest discover tests
```