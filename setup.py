import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '1.0.0'
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
    'beautifulsoup4==4.12.3',
    'certifi==2024.12.14',
    'charset-normalizer==3.4.1',
    'idna==3.10',
    'numpy==2.0.2',
    'pandas==2.2.3',
    'pyarrow==19.0.0',
    'openpyxl==3.1.5',
    'python-dateutil==2.9.0.post0',
    'pytz==2024.2',
    'requests==2.32.3',
    'setuptools==75.8.0',
    'six==1.17.0',
    'soupsieve==2.6',
    'tqdm==4.67.1',
    'tzdata==2025.1',
    'urllib3==2.3.0',
    'PyYAML==6.0.2'
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
