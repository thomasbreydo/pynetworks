from setuptools import setup, find_packages


def get_long_description():
    with open('README.md') as readme:
        return readme.read()


setup(
    name='pynetworks',
    version='0.4.0',
    author='Thomas Breydo',
    author_email='tbreydo@gmail.com',
    description='A Python implementation for networks of nodes.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    license='GNU',
    url='https://github.com/thomasbreydo/pynetworks',
    include_package_data=True
)
