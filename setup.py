

# build with 'python ./setup.py install'
from distutils.core import setup

VERSION = "0.0.3"

setup(
    name = 'carp-rpc',
    version = VERSION,
    license = 'MIT',
    description = 'Async RPC toolkit',
    author = 'Bill Gribble',
    author_email = 'grib@billgribble.com',
    url = 'https://github.com/bgribble/carp',
    download_url = 'https://github.com/bgribble/carp/archive/refs/tags/v0.0.2.tar.gz',
    keywords = ['rpc', 'protobuf', 'json'],
    install_requires = [
        "protobuf", "python-dateutil",
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
