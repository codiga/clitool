# Code-Inspector Continuous Integration Tool

This is a Python tool used to trigger new analysis on [code-inspector](https://www.code-inspector.com)
in continuous integration pipeline.


## Build


## Usage

You need to set your API keys with environment variables:

 * `CODE_INSPECTOR_ACCESS_KEY`: your access key API generated from your project preferences
 * `CODE_INSPECTOR_SECRET_KEY`: your secret key API generated from your project preferences

On a terminal, you would set them up like this:
```bash
export CODE_INSPECTOR_ACCESS_KEY=<INSERT-YOUR-API-ACCESS-KEY-HERE>
export CODE_INSPECTOR_SECRET_KEY=<INSERT-YOUR-API-SECRET-KEY-HERE>
```

Then, just invoke the tool as follow:

```python 
code-inspector
```

If a new build is triggered, the tool returns 0. If any issue occurs, it will return a non-zero value.

If you get non-zero return code and want to investigate, use the `-verbose` flag and invoke the tool as follow:

```python 
code-inspector --verbose
```


## About Code Inspector

[Code Inspector](https://www.code-inspector.com) is a software analysis platform to manage and mitigate
technical debt. It offers plans that caters to all developers. From our basic free plan for your personal project
to the gold plan (for companies with multiples private projects), [code-inspector](https://www.code-inspector.com) detects coding issues
and helps you keep your project afloat.
