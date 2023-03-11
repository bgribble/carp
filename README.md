CARP -- Async RPC tools

`carp` started with an RPC system I built for
[`mfp`](https://github.com/bgribble/mfp), a real-time audio
environment inspired by MAX/MSP and
[PureData](https://github.com/pure-data/pure-data). I was writing
in GIL-constrained Python and needed to be able to take advantage
of multiple cores efficiently. `multiprocessing` was a good
starting point for ganging up multiple Python runtimes to work on
different parts of a problem, but it didn't really give much
guidance about how to communicate between processes in a clean
way. So an RPC system of some kind was needed. I hacked one
together and it was fine, but it always annoyed me and I wanted
something better.

[`tinyrpc`](https://github.com/mbr/tinyrpc) basically does
everything you could want it to do, so why not just use that? The
main thing is that I am interested in doing it using Python's
asyncio framework and want to build it from the ground up that
way. Also I like building my own tools.

### Status

I am making a release of Carp so I can upload it to PyPi for use
in my own other packages. It's ready enough for that but not
complete by any stretch. Only the UNIX socket channel type is
implemented (that's all I need right now). I would definitely not
use it for anything beyond a toy right now.

### carp.channel

carp.channel.Channel is a message-oriented API for sending and receiving
data. Subclasses implement the API for different channel types:

* Unix-domain sockets (carp.channel.UnixSocketChannel)
* [TBD] Inet sockets (carp.channel.InetSocketChannel)
* [TBD] SysV shared memory segments (carp.channel.ShmChannel)

### carp.serializer

Data to be sent over a `channel` must be serialized. The goal
here is to support efficient serializers like protobuf or msgpack
but fall back to good old JSON.

Serialized messages are tagged with the serializer name to assist
with deserialization.

`Serializable` is a mixin class which allows the `serialize` and
`deserialize` methods to be overridden.

### carp.service

carp.service contains helper classes and decorators for defining
RPC services in user code.

* carp.service.apiclass -- class decorator for class-oriented APIs
* carp.service.apifunc -- decorator for function-oriented APIs

### carp.host

carp.host includes the Host type, which is the main interface
object for carp and operates the main message processing loop.
There is one Host instance per RPC node. Host has key methods
including:

* `export(service)` to announce a RPC service is available
* `require(service)` to use a service exported by another node
* `call(service, *args, **kwargs)` to marshal arguments for an
  RPC call, send them, and await a response
