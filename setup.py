import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'dowski.scoreboard'
DESCRIPTION = 'Source code that powers my electronic scoreboard'
URL = 'https://github.com/dowski/scoreboard'
EMAIL = 'christian@dowski.com'
AUTHOR = 'Christian Wyglendowski'
REQUIRES_PYTHON = '>=2.7.0, <2.8.0'
VERSION = '0.9.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'mlbgame',
]

REQUIRED_FOR_TESTS = [
    'pytest',
    'mock',
]

REQUIRED_FOR_SETUP = [
    'pytest-runner',
]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
#with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
#    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    #long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    setup_requires=REQUIRED_FOR_SETUP,
    tests_require=REQUIRED_FOR_TESTS,
    include_package_data=True,
    license='Proprietary',
)
