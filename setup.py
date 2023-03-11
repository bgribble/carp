

# build with 'python ./setup.py install'
from distutils.core import setup

VERSION = "0.0.1"

setup(
    name = 'carp-rpc',
    packages = ['carp'],
    version = VERSION,
    license = 'MIT',
    description = 'Async RPC toolkit',
    author = 'Bill Gribble',
    author_email = 'grib@billgribble.com',
    url = 'https://github.com/bgribble/carp',
    download_url = 'https://github.com/bgribble/carp/archive/refs/tags/v0.0.1.zip',
    keywords = ['rpc', 'protobuf', 'json'],
    install_requires = [
        "protobuf",
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
