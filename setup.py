from setuptools import setup, find_packages
from codecs import open
from os import path

from sphinxview.sphinxview import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='sphinxview',
    version=__version__,
    packages=find_packages(exclude=['tests']),
    description='Serves your Sphinx project and reloads pages on source changes',
    long_description=long_description,
    url='https://github.com/trarbr/sphinxview',
    author='Troels Brødsgaard',
    author_email='tr@arbr.dk',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    keywords='sphinx',
    install_requires=requirements,
    package_data={
        'sphinxview': ['sphinxview.js'],
    },
    entry_points={
        'console_scripts': ['sphinxview=sphinxview.sphinxview:main'],
    },
)
