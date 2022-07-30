import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent


VERSION = "1.0.1"
PACKAGE_NAME = "obsstudio_sdk"
AUTHOR = "Adem Atikturk"
AUTHOR_EMAIL = "aatikturk@gmail.com"
URL = "https://github.com/aatikturk/obsstudio_sdk"
LICENSE = "GNU General Public License v3.0"
DESCRIPTION = "A Python SDK for OBS Studio WebSocket v5.0"


LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

# Dependencies for the package
INSTALL_REQUIRES = ["websocket-client"]

# Development dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest",
        "pytest-randomly",
        "black",
        "isort",
    ]
}

# Python version requirement
PYTHON_REQUIRES = ">=3.11"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=PYTHON_REQUIRES,
    packages=find_packages(),
)
