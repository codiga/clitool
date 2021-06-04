import os

from setuptools import setup, find_packages


VERSION_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'code_inspector', 'version.py')

DESCRIPTION = open('README.md').read()

VERSION = None
with open(VERSION_FILE, 'r') as f:
    VERSION = f.read().split()[2][1:-1]


setup(
    name='code-inspector',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/codeinspectorio/citool',
    project_urls={
        'Changelog': ('https://github.com/codeinspectorio/citool/'
                      'blob/master/CHANGELOG.md'),
        'Docs': 'https://github.com/codeinspectorio/citool/',
    },
    license='BSD',
    author='code-inspector',
    description='Trigger new code analysis on code-inspector.io',
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'code-inspector-analyze = code_inspector.analyze:main',
            'code-inspector-github-action = code_inspector.github_action:main',
            'code-inspector-check-quality = code_inspector.check_quality:main',
            'code-inspector-pre-hook-check = code_inspector.pre_hook_check:main',
            'code-inspector-compare = code_inspector.compare:main',
            'code-inspector-project = code_inspector.project:main'
        ],
    },
    install_requires=['docopt>=0.6.2', 'requests>=2.25.1', "unidiff>=0.6.0", "tenacity>=7.0.0"],
    extras_require={
        'yaml': ['PyYAML>=3.10'],
        ':python_version < "3"': ['urllib3[secure]'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Testing',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
