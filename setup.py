import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'requests>=2.9.1',
    'xmltodict>=0.13.0',
    'cryptography>=3.4',
]

testing_requires = [
    'flake8',
    'pytest',
    'pytest-cov',
]

setup(
    name='wechat_pay',
    version='1.2',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=install_requires,
    extras_require={'testing': testing_requires},
    license='GNU General Public License v3 (GPLv3)',
    description='Wechat payments module',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://www.vericant.com/',
    author='vericant',
    author_email='tech@vericant.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ])
