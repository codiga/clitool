import os

from setuptools import setup


VERSION_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'code_inspector', 'version.py')

DESCRIPTION = open('README.md').read()

VERSION = None
with open(VERSION_FILE, 'r') as f:
    VERSION = f.read().split()[2][1:-1]


setup(
    name='code-inspector',
    version=VERSION,
    packages=['code_inspector'],
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
    entry_points={
        'console_scripts': [
            'code-inspector = code_inspector.cli:main',
        ],
    },
    install_requires=['docopt>=0.6.1', 'requests>=2.4.2'],
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)