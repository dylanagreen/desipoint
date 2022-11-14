import os, sys, glob, re
from setuptools import setup, find_packages

def _get_version():
    line = open('desipoint/_version.py').readline().strip()
    m = re.match("__version__\s*=\s*'(.*)'", line)
    if m is None:
        print('ERROR: Unable to parse version from: {}'.format(line))
        version = 'unknown'
    else:
        version = m.groups()[0]

    return version

setup_keywords = dict(
    name='desipoint',
    version=_get_version(),
    description='Package for working with DESI all-sky images',
    url='https://github.com/dylanagreen/desipoint',
    author='Dylan Green',
    author_email='dylanag@uci.edu',
    license='BSD 3-Clause',
    packages=find_packages(),
    install_requires=['numpy', 'astropy', 'requests', 'matplotlib', 'Pillow'],
    zip_safe=False,
    include_package_data=True,
)

setup(**setup_keywords)