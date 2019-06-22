# Code-Inspector Continuous Integration Tool


These are various Python tools used to use the [code-inspector](https://www.code-inspector.com)
engine in a continuous integration pipeline and compare analysis.

The following programs are being included:

 * `code-inspector-compare`: compare a project metrics against another projects or branches


## Build

You can build and try the program using the following command:

```bash
python setup.py install --user
```

You will then find binaries in `$HOME/.local/bin`, for example `$HOME/.local/bin/code-inspector-compare`.

## Usage

You need to set your API keys with environment variables:

 * `CODE_INSPECTOR_ACCESS_KEY`: your access key API generated from your project preferences
 * `CODE_INSPECTOR_SECRET_KEY`: your secret key API generated from your project preferences

On a terminal, you would set them up like this:
```bash
export CODE_INSPECTOR_ACCESS_KEY=<INSERT-YOUR-API-ACCESS-KEY-HERE>
export CODE_INSPECTOR_SECRET_KEY=<INSERT-YOUR-API-SECRET-KEY-HERE>
```

### Compare tool

The compare tool is used to compare a project with another repository. 
Invoke the tool as follow:

```python 
code-inspector-compare -p "mergify integration" --kind <REPOSITORY_KIND> --url <URL_TO_OTHER_REPOSITORY> --target-branch=<BRANCH> --target-revision=<REVISION>
```

This command will compare the project `mergify integration` on code inspector with the project located
at the URL `<URL_TO_OTHER_REPOSITORY>`.

These are the explanation for the other parameters:
 * `kind`: kind of repository used for the target. Can be `Git`, `Github`, `Gitlab` or `Bitbucket`. Values are explained below. This parameter is **REQUIRED**.
 * `URL`: URL of the repository. This parameter is **REQUIRED**.
 * `target-revision`: revision of the target repository. This parameter is **OPTIONAL**
 * `target-branch`: branch of the target repository. This parameter is **OPTIONAL**
 

If you get non-zero return code and want to investigate, use the `-verbose` flag and invoke the tool as follow:

```python 
code-inspector-compare --verbose
```


## About Code Inspector

[Code Inspector](https://www.code-inspector.com) is a software analysis platform to manage and mitigate
technical debt. It offers plans that caters to all developers. From our basic free plan for your personal project
to the gold plan (for companies with multiples private projects), [code-inspector](https://www.code-inspector.com) detects coding issues
and helps you keep your project afloat.
