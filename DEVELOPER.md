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

### Publishing new version

1. Bump the version in `codiga/version.py` on the master branch
2. Commit the code `git commit -a && git push`
3. Draft a new release
   - Go on https://github.com/codiga/clitool/releases
   - Choose/create a tag for the release and match the version number set above (vX.X.X)
   - add a detailed log of what's changed
   - Publish release
