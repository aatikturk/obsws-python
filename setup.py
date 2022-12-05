import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent


def get_version():
    versionpath = pathlib.Path(HERE) / "obsws_python" / "version.py"
    with open(versionpath) as f:
        for line in f:
            if line.startswith("version"):
                versionstring = line.split('"')[1]
    return versionstring


VERSION = get_version()
PACKAGE_NAME = "obsws-python"
AUTHOR = "Adem Atikturk"
AUTHOR_EMAIL = "aatikturk@gmail.com"
URL = "https://github.com/aatikturk/obsws-python"
LICENSE = "GNU General Public License v3.0"
DESCRIPTION = "A Python SDK for OBS Studio WebSocket v5.0"


LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

# Dependencies for the package
INSTALL_REQUIRES = ["websocket-client", "tomli >= 2.0.1;python_version < '3.11'"]

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
PYTHON_REQUIRES = ">=3.9"

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
