import sys

from setuptools import setup, find_packages

from photostash import __version__


install_requires = [
    'clint',
    'tastypie-queryset-client',
    'slumber',
    'requests',
]

if sys.version_info < (2, 7):
    install_requires.append('argparse==1.1')


setup(
    name='photostash-client',
    version=__version__,
    description='Official photostash command line client',
    url='https://github.com/seanbrant/photostash-client',
    author='Sean Brant',
    author_email='brant.sean@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'stash = photostash.cli:main',
        ],
    },
    install_requires=install_requires,
)
