# setup.py

from setuptools import setup

# read requirements.txt as use as install_requires
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='chatgpt_tooling',
    version='0.0.1',
    packages=[
        'chatgpt_tooling',
    ],
    install_requires=install_requires,
)
