Network Gateway Interface
*************************

The Network Gateway Interface provides:

- the ability to test application networking code without use of
  sockets, threads or subprocesses

- clean separation of application code and low-level networking code

- a fairly simple inheritence free set of networking APIs

- an event-based framework that makes it easy to handle many
  simultaneous connections while still supporting an imperative
  programming style.

To learn more, see http://packages.python.org/zc.ngi/

Changes
*******

==================
1.1.3 (2009-07-30)
==================

Bug fixed:

- zc.ngi.async bind failures weren't handled properly, causing lots of
  annoying log messages to get spewed, which tesnded to fill up log
  files.

==================
1.1.2 (2009-07-02)
==================

Bugs fixed:

- The zc.ngi.async thread wasn't named. All threads should be named.

==================
1.1.1 (2009-06-29)
==================

Bugs fixed:

- zc.ngi.blocking didn't properly handle connection failures.

==================
1.1.0 (2009-05-26)
==================

Bugs fixed:

- Blocking input and output files didn't properly synchronize closing.

- The testing implementation made muiltiple simultaneous calls to
  handler methods in violation of the promise made in interfaces.py.

- Async TCP servers used too low a listen depth, causing performance
  issues and spurious test failures.

New features:

- Added UDP support.

- Implementation responsibilities were clarified through an
  IImplementation interface.  The "connector" attribute of the testing
  and async implementations was renamed to "connect". The old name
  still works.

- Implementations are now required to log handler errors and to close
  connections in response to connection-handler errors. (Otherwise,
  handlers, and especially handler adapters, would have to do this.)

==================
1.0.1 (2007-05-30)
==================

Bugs fixed:

- Server startups sometimes failed with an error like::

    warning: unhandled read event
    warning: unhandled write event
    warning: unhandled read event
    warning: unhandled write event
    ------
    2007-05-30T22:22:43 ERROR zc.ngi.async.server listener error
    Traceback (most recent call last):
      File "asyncore.py", line 69, in read
        obj.handle_read_event()
      File "asyncore.py", line 385, in handle_read_event
        self.handle_accept()
      File "/zc/ngi/async.py", line 325, in handle_accept
        sock, addr = self.accept()
    TypeError: unpack non-sequence
