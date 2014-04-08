from __future__ import absolute_import
from setuptools import setup
from mesos_marathon import __version__

setup(
    name='py_marathon',
    version=__version__,
    packages=['mesos_marathon'],
    url='https://github.com/zircote/py_marathon',
    license='Apache-2.0',
    author='Robert Allen',
    author_email='zircote@gmail.com',
    description='A wrapper for Mesos Framework Marathons API interface.',
    install_requires=[
        "httplib2",
        "termcolor"
    ],
    entry_points={
        'console_scripts': [
            'mesos-marathon = mesos_marathon.cli:main',
        ]
    }
)
