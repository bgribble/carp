

# build with 'python ./setup.py install'
from setuptools import setup

def shcall(cmdline):
    from subprocess import Popen,PIPE
    return Popen(cmdline.split(), stdout=PIPE).communicate()[0].decode()

def git_version():
    vers = shcall(b"git show --oneline").split('\n')[0].split(' ')[0]
    if not isinstance(vers, str):
        vers = vers.decode()
    return 'git_' + str(vers.strip())

setup(
    name = 'carp',
    version = '0.01+' + git_version(),
    description = 'Async RPC toolkit',
    packages = ['carp'],

)
