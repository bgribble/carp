CARP -- modular asyncio RPC subsystem

`carp` started with an RPC system I built for `mfp`, a real-time
audio environment inspired by MAX/MSP and PureData. I was writing
in GIL-constrained Python and needed to be able to take advantage
of multiple cores efficiently. `multiprocessing` was a good
starting point for ganging up multiple Python runtimes to work on
different parts of a problem, but it didn't really give much
guidance about how to communicate between processes in a clean
way. So an RPC system of some kind was needed. 

### carp.channel

carp.channel.Channel is a message-oriented API for sending and receiving
data. Subclasses implement the API for 

* Unix-domain sockets (carp.UnixSocketChannel)
* Inet sockets (carp.InetSocketChannel)
* SysV shared memory segments (carp.ShmChannel)

### carp.serializer

carp.serializer.Serializer implements message conversion to and from byte
array. 

* carp.serializer.JsonSerializer
* carp.serializer.MsgPackSerializer
* carp.serializer.ProtoBufSerializer

### carp.service

carp.service contains helper classes and decoreators for defining
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

