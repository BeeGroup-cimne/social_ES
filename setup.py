import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.0'
PACKAGE_NAME = 'social_ES'
AUTHOR = 'Jose Manuel Broto Vispe'
AUTHOR_EMAIL = 'jmbrotovispe@gmail.com'
URL = 'https://github.com/BeeGroup-cimne'

LICENSE = 'MIT'
DESCRIPTION = 'Python library to obtain the Spanish socioeconomic data joined with INE and OpenDataBCN sources.'
LONG_DESCRIPTION = (HERE / "README.md").read_text(
    encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'numpy==1.24.3',
    'pandas==2.0.2',
    'requests==2.30.0',
    'beautifulsoup4==4.10.0',
    'tqdm==4.64.1',
    'PyYAML==5.4.1'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)
