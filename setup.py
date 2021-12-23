from __future__ import unicode_literals, absolute_import
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'requests>=2.9.1',
    'pycrypto==2.6.1',
    'xmltodict==0.10.1',
    'cryptography>=2.5',
]

testing_requires = [
    'flake8',
    'pytest',
    'pytest-cov',
]

setup(
    name='wechat_pay',
    version='0.4beta4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license='GNU General Public License v3 (GPLv3)',
    description='Wechat payments module',
    long_description=README,
    url='https://www.vericant.com/',
    author='murchik',
    author_email='murchik@protonmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ])
