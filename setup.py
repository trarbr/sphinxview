from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sphinxview',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),

    description='Serves your Sphinx project and reloads pages on source changes',
    long_description=long_description,
    url='https://github.com/trarbr/sphinxview',
    author='Troels Brødsgaard',
    author_email='tr@arbr.dk',
    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    keywords='sphinx',

    install_requires=['sphinx', 'docopt'],

    # TODO: figure out how to copy this automagically into _static on cli (so also must extend interface)
    package_data={
        'sphinxview': ['sphinxview.js'],
    },
    entry_points={
        'console_scripts': ['sphinxview=sphinxview.sphinxview:main'],
    },
)
