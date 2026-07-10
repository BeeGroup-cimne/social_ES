import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '1.0.1'
PACKAGE_NAME = 'social_ES'
AUTHOR = 'Jose Manuel Broto Vispe'
AUTHOR_EMAIL = 'jmbrotovispe@gmail.com'
URL = 'https://github.com/BeeGroup-cimne/social_ES'

DESCRIPTION = ('Python library to ingest, clean, and transform up-to-date Spanish '
               'demographic, socioeconomic, and other social-related datasets from '
               'the National Statistics Institute (INE) and other sources.')
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

# Only the direct runtime dependencies of social_ES/INE.py, with loose floors so
# the library does not force conflicting versions on downstream users.
INSTALL_REQUIRES = [
    'pandas>=2.0',
    'requests>=2.31',
    'beautifulsoup4>=4.12',
    'tqdm>=4.66',
    'numpy>=1.26',
    'scipy>=1.11',
    'pyarrow>=14',
    'openpyxl>=3.1',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
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
    license='EUPL-1.2',
    license_files=['LICENSE'],
    python_requires='>=3.9',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    project_urls={
        'Source': URL,
        'Bug Tracker': f'{URL}/issues',
    },
)
