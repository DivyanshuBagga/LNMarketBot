from setuptools import setup, find_packages
import sys


if sys.version_info < (3, 6):
    raise RuntimeError("This package requres Python 3.6+")
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='LNMarketBot',
    packages=find_packages(include=['LNMarketBot']),
    version='0.2.0',
    description='Trading Bot for LNMarkets',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DivyanshuBagga/LNMarketBot",
    author='Divyanshu Bagga',
    author_email="divyanshu.baggar@pm.me",
    license='MIT',
    install_requires=[
        'requests',
        'krakenex',
        'pykrakenapi',
        'LNMarkets',
        'notifiers',
    ],
    download_url='https://github.com/DivyanshuBagga/LNMarketBot/archive/'
    '0.2.0.tar.gz',
    keywords=['Bitcoin', 'Finance', 'Trading'],
    python_requires='>=3.6',
)
