

# build with 'python ./setup.py install'
from distutils.core import setup

def shcall(cmdline):
    from subprocess import Popen,PIPE
    return Popen(cmdline.split(), stdout=PIPE).communicate()[0].decode()

def git_version():
    vers = shcall(b"git show --oneline").split('\n')[0].split(' ')[0]
    if not isinstance(vers, str):
        vers = vers.decode()
    return str(int(vers.strip(), 16))

VERSION = "0.0.1"

setup(
    name = 'carp-rpc',
    packages = ['carp'],
    version = VERSION,
    license = 'MIT',
    description = 'Async RPC toolkit',
    author = 'Bill Gribble',
    author_email = 'grib@billgribble.com',
    uri = 'https://github.com/bgribble/carp',
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
