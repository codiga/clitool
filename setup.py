import os

from setuptools import setup, find_packages


VERSION_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'codiga', 'version.py')

DESCRIPTION = open('README.md').read()

VERSION = None
with open(VERSION_FILE, 'r') as f:
    VERSION = f.read().split()[2][1:-1]


setup(
    name='codiga',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/codeinspectorio/citool',
    project_urls={
        'Changelog': ('https://github.com/codiga/clitool/'
                      'blob/master/CHANGELOG.md'),
        'Docs': 'https://github.com/codiga/clitool/',
    },
    license='BSD',
    author='codiga',
    description='CLI tools for codiga.io',
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'codiga-analyze = codiga.analyze:main',
            'codiga-github-action = codiga.github_action:main',
            'codiga-check-quality = codiga.check_quality:main',
            'codiga-pre-hook-check = codiga.pre_hook_check:main',
            'codiga-compare = codiga.compare:main',
            'codiga-project = codiga.project:main'
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
