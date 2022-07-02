CARP -- modular asyncio RPC subsystem

`carp` started with an RPC system I built for `mfp`, a real-time
audio environment inspired by MAX/MSP and PureData. I was writing
in GIL-constrained Python and needed to be able to take advantage
of multiple cores efficiently. `multiprocessing` was a good
starting point for ganging up multiple Python runtimes to work on
different parts of a problem, but it didn't really give much
guidance about how to communicate between processes in a clean
way. So an RPC system of some kind was needed. 

`tinyrpc` basically does everything you could want it to do, so
why not just use that? The main thing is that I am interested in
doing it using Python's asyncio framework and want to build it
from the ground up that way.

NOT COMPLETE OR READY FOR USE YET -- STILL ACTIVELY DEVELOPING

### carp.channel

carp.channel.Channel is a message-oriented API for sending and receiving
data. Subclasses implement the API for 

* Unix-domain sockets (carp.channel.UnixSocketChannel)
* Inet sockets (carp.channel.InetSocketChannel)
* SysV shared memory segments (carp.channel.ShmChannel)

### carp.serializer

carp.serializer.Serializable is a mixin that implements message
conversion to and from byte array. The default serializer uses
JSON, and requires the implementation of a `to_dict()` and a
`from_dict()` method for the class. Serializers can be different
per-class; the serialized reperesentation is tagged.

### carp.service

carp.service contains helper classes and decorators for defining
RPC services in user code 

* carp.service.APIClass -- base class for class-oriented APIs
* carp.service.apimethod -- method decorator for published
  methods on APIClasses
* carp.service.apistaticmethod -- static method decorator for
  APIClasses
* carp.service.apifunc -- decorator for function-oriented APIs

### carp.host 

carp.host contains classes for managing client and server ends of
an RPC connection. 



