from __future__ import unicode_literals, absolute_import
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'requests>=2.9.1',
    # 'pycrypto==2.6.1',  # python 3.5/6
    'pycryptodome',  # python 3.10
    'xmltodict>=0.13.0',
    'cryptography>=2.5',
]

testing_requires = [
    'flake8',
    'pytest',
    'pytest-cov',
]

setup(
    name='wechat_pay',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license='GNU General Public License v3 (GPLv3)',
    description='Wechat payments module',
    long_description=README,
    url='https://www.vericant.com/',
    author='vericant',
    author_email='tech@vericant.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ])
