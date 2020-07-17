from setuptools import setup
import re

with open("pynetworks/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    install_requires=[
        'pyperclip>=1.8.0',
    ],
    version=version,
)  # Metadata is in setup.cfg
