""" This module contains the Stream class. The
Stream and Agent classes are the building blocks
of PythonStreams.
(Modified 2015_09_07_15_05, Added _close. Mani)
"""

from SystemParameters import DEFAULT_STREAM_SIZE,\
                             DEFAULT_BUFFER_SIZE_FOR_STREAM
# Import numpy and pandas if StreamArray (numpy) and StreamSeries (Pandas)
# are used.
import numpy as np
import pandas as pd
from collections import namedtuple

# TimeAndValue is used for timed messages.
TimeAndValue = namedtuple('TimeAndValue', ['time', 'value'])

# _no_value is the message sent on a stream to indicate that no
# value is sent on the stream at that point. _no_value is used
# instead of None because a message with value None may be
# meaningful.
_no_value = object

# _close is the message sent on a stream to indicate that the
# stream is closed.
_close = object


class _multivalue(object):
    def __init__(self, lst):
        self.lst = lst


class Stream(object):
    """
    A stream is a sequence of values. Agents can:
    (1) Append values to the tail of stream and
    close a stream.
    (2) Read a stream.
    (3) Subscribe to be notified when a
    value is added to a stream.
    (See Agent.py for details of agents.)

    The ONLY way in which a stream can be
    modified is that values can be appended to its
    tail. The length of a stream (number of elements
    in its sequence) can stay the same or increase,
    but never decreases. If at some point, the length
    of a stream is k, then from that point onwards, the
    first k elements of the stream remain unchanged.

    A stream is written by only one agent. Any
    number of agents can read a stream, and any
    number of agents can subscribe to a stream.
    An agent can be a reader and a subscriber and
    a writer of the same stream. An agent may subscribe
    to a stream without reading the stream's values; for
    example the agent may subscribe to a clock stream
    and the agent executes a state transition when the
    the clock stream has a new value, regardless of
    the value.

    Parameters
    ----------
    name : str, optional
          name of the stream. Though the name is optional
          a named stream helps with debugging.
          default : 'NoName'
    proc_name : str, optional
          The name of the process in which this agent
          executes.
          default: 'UnknownProcess'
    initial_value : list or array, optional
          The list (or array) of initial values in the
          stream.
          default : []
    stream_size: int, optional
          stream_size must be a positive integer.
          It is the largest number of the most recent
          elements in the stream that are in main memory.
          default : DEFAULT_STREAM_SIZE
                    where DEFAULT_STREAM_SIZE is
                    specified in SystemParameters.py
    buffer_size : int, optional
           buffer_size must be a positive integer.
           An exception may be thrown if an agent reads an
           element with index i in the stream where i is
           less than the length of the stream - buffer_size.
           default : DEFAULT_BUFFER_SIZE_FOR_STREAM
                     specified in SystemParameters.py

    Attributes
    ----------
    recent : list
          A list of the most recent values of the stream.
          recent is a NumPy array if specified.
    stop : int
          index into the list recent.
          s.recent[:s.stop] contains the s.stop most recent
          values of stream s.
          s.recent[s.stop:] contains padded values.
    offset: int
          index into the stream used to map the location of
          an element in the entire stream with the location
          of the same element in s.recent, which only
          contains the most recent elements of the stream.
          For a stream s:
                   s.recent[i] = s[i + s.offset]
                      for i in range(s.stop)
    start : dict of readers.
            key = reader
            value = start index of the reader
            Reader r can read the slice:
                      s.recent[s.start[r] : s.stop ]
            in s.recent which is equivalent to the following
            slice in the entire stream:
                    s[s.start[r]+s.offset: s.stop+s.offset]
    subscribers_set: set
             the set of subscribers for this stream.
             Subscribers are agents to be notified when an
             element is added to the stream.
    closed: boolean
             True if and only if the stream is closed.
             An exception is thrown if a value is appended to
             a closed stream.
    _buffer_size: int
            Invariant:
            For every reader r of stream s:
                 s.stop - s.start[r] < s._buffer_size
            A reader can only access _buffer_size number of
            consecutive, most recent, elements in the stream.
    _begin : int
            index into the list, recent
            recent[:_begin] is not being accessed by any reader;
            therefore recent[:_begin] can be deleted from main
            memory.
            Invariant:
                    for all readers r:
                          _begin <= min(start[r])

    Notes
    -----
    1. AGENTS SUBSCRIBING TO A STREAM

    An agent is a state-transition automaton and
    the only action that an agent executes is a
    state transition. If agent x is a subscriber
    to a stream s then x.next() --- a state
    transition of x --- is invoked whenever messages
    are appended to s.

    The only point at which an agent executes a
    state transition is when a stream to which
    the agent subscribes is modified.

    An agent x subscribes to a stream s by executing
            s.call(x).
    An agent x unsubscribes from a stream s by
    executing:
            s.delete_caller(x)


    2. AGENTS READING A STREAM

    2.1 Agent registers for reading

    An agent can read a stream only after it registers
    with the stream as a reader. An agents r registers
    with a stream s by executing:
                   s.reader(r)
    An agent r deletes its registration for reading s
    by executing:
                   s.delete_reader(r)

    2.2 Slice of a stream that can be read by an agent

    At any given point, an agent r that has registered
    to read a stream s can only read some of the most
    recent values in the stream. The number of values
    that an agent can read may vary from agent to agent.
    A reader r can only read a slice:
             s[s.start[r]+s.offset: s.stop+s.offset]
    of stream s where start[r], stop and offset are
    defined later.


    3. WRITING A STREAM

    3.1 Extending a stream

    When an agent is created it is passed a list
    of streams that it can write.

    An agent adds a single element v to a stream s
    by executing:
                  s.append(v)

    An agent adds the sequence of values in a list
    l to a stream s by executing:
                   s.extend(l)
    The operations append and extend of streams are
    analogous to operations with the same names on
    lists.

    3.2 Closing a Stream

    A stream is either closed or open.
    Initially a stream is open.
    An agent that writes a stream s can
    close s by executing:
                  s.close()
    A closed stream cannot be modified.

    4. MEMORY

    4.1 The most recent values of a stream

    The most recent elements of a stream are
    stored in main memory. In addition, the
    user can specify whether all or part of
    the stream is saved to a file.

    Associated with each stream s is a list (or
    array) s.recent that includes the most
    recent elements of s. If the value of s is a
    sequence:
                  s[0], ..., s[n-1],
    at a point in a computation then at that point,
    s.recent is a list
                    s[m], .., s[n-1]
    for some m, followed by some padding (usually
    a sequence of zeroes, as described later).

    The system ensures that all readers of stream
    s only read elements of s that are in s.recent.

    4.2 Slice of a stream that can be read

    Associated with a reader r of stream s is an
    integer s.start[r]. Reader r can only read
    the slice:
               s.recent[s.start[r] : ]
    of s.recent.

    For readers r1 and r2 of a stream s the values
    s.start[r1] and s.start[r2] may be different.

    4.3 When a reader finishes reading part of a stream

    Reader r informs stream s that it will only
    read values with indexes greater than or
    equal to j in the list, recent,  by executing
                  s.set_start(r, j)
    which causes s.start[r] to be set to j.


    5. OPERATION

    5.1 Memory structure

    Associated with a stream is:
    (1) a list, recent.
    (2) a nonnegative integer stop  where:
       (a) recent[ : stop] contains
           the most recent values of the stream,
       (b) the slice recent[stop:] is
           padded with padding values
           (either 0 or 0.0).
    (3) a nonnegative integer s.offset where
          recent[i] = stream[i + offset]
             for 0 <= i < s.stop

    Example: if the sequence of values in  a stream
    is:
               0, 1, .., 949
    and s.offset is 900, then
       s.recent[i] = s[900+i] for i in 0, 1, ..., 49.

    Invariant:
              len(s) = s.offset + s.stop
    where len(s) is the number of values in stream s.

    The size of s.recent is the parameter stream_size
    of s. Recommendations for the value of stream_size
    are given after a few paragraphs.

    The maximum size of the list that an agent can
    read is the parameter, buffer_size. Set
    buffer_size large enough so that the size of
    the slice that any agent wants to read is less
    than buffer_size. If an agent is slow compared to
    the rate at which the stream grows then the
    buffer_size should be large. For example, if
    an agent is reading the element in the stream
    at location i, and the stream has grown to l
    elements then buffer_size must be greater than
    l - i.

    (In later implementations, if an agent reads
    a part of stream s that is not in s.recent, then
    the value read is obtained from values saved to
    a file.)

    The entire stream, or the stream up to offset,
    can be saved in a file for later processing.
    You can also specify that no part of the stream
    is saved to a file. (Note, if the stream s is not
    saved, and any agent reads an element of the
    stream s that is not in main memory, then an
    exception is raised.)

    In the current implementation old values of the
    stream are not saved.

    5.2 Memory Management

    We illustrate memory management with the
    following example with stream_size=4 and
    buffer_size=1

    Assume that a point in time, for a stream s,
    the list of values in the stream is
    [1, 2, 3, 10, 20]; stream_size=4;
    s.offset=3; s.stop=2; and
    s.recent = [10, 20, 0, 0].
    The size s.recent is stream_size (i.e. 4).
    The s.stop (i.e. 2) most recent values in the
    stream are 10 followed by a later value, 20.
    s[3] == 10 == s.recent[0]
    s[4] == 20 == s.recent[1]
    The values  in s.recent[s.stop:] are padded
    values (zeroes).

    A reader r of stream s has access to the list:
      s.recent[s.start[r] : s.stop]
    So, if for a reader r, s.start[r] is 0,
    then r has access to the two most
    recent values in the stream, i.e.,
    the list [10, 20].
    If for another reader q, s.start[q]=1,
    then q has access to the list [20].
    And for another reader u, s.start[q]=2,
    then u has access to the empty list [].

    When a value v is appended to stream s, then
    v is inserted in s.recent, replacing a padded
    value, and s.stop is incremented. If the empty
    space (i.e., the number of padded values) in
    s.recent decreases below buffer_size then a
    new version of s.recent is created containing
    only the buffer_size most recent values of the
    stream.

    Example: Start with the same example as the previous
    example with buffer_size = 2

    Then a new value, 30 is appended to the stream,
    making the list of values in s:
    [1, 2, 3, 10, 20, 30]
    s.stop = 3; s.offset is unchanged (i.e. 3) and
    s.recent = [10, 20, 30, 0].
    Now the size of the empty space in s.recent is 1,
    which is less than buffer_size. So, the program sets
    s.recent to [20, 30, 0, 0], keeping the buffer_size
    (i.e. 2) most recent values in s.recent and removing
    older values from main memory, and it sets s.stop to
    buffer_size, and increments offset by
    s.stop - buffer_size. Now
       s.stop = 2
       s.offset = 4

    """
    def __init__(self, name="NoName", proc_name="UnknownProcess",
                 initial_value=[],
                 stream_size=DEFAULT_STREAM_SIZE,
                 buffer_size=DEFAULT_BUFFER_SIZE_FOR_STREAM):
        self.name = name
        # Name of the process in which this stream lives.
        self.proc_name = proc_name
        # Create the list recent and the parameters
        # associated with garbage collecting
        # elements in the list.
        # Pad recent with any padded value (e.g. zeroes).
        self.recent = [0] * stream_size
        self._buffer_size = buffer_size
        self._begin = 0
        # Initially, the stream has no entries, and so
        # offset and stop are both 0.
        self.offset = 0
        self.stop = 0
        # Initially the stream has no readers.
        self.start = dict()
        # Initially the stream has no subscribers.
        self.subscribers_set = set()
        # Initially the stream is open
        self.closed = False
        assert (isinstance(initial_value, list) or
                isinstance(initial_value, np.ndarray))

    def reader(self, reader, start_index=0):
        """
        Register a reader.

        The newly registered reader starts reading list recent
        from index start, i.e., reads the slice
        recent[start_index:s.stop]
        If reader has already been registered with this stream
        its start value is updated to the parameter in the call.
        """
        self.start[reader] = start_index

    def delete_reader(self, reader):
        """
        Delete this reader from this stream.
        """
        if reader in self.start:
            del self.start[reader]

    def call(self, agent):
        """
        Register a subscriber for this stream.
        """
        self.subscribers_set.add(agent)

    def delete_caller(self, agent):
        """
        Delete a subscriber for this stream.
        """
        self.subscribers_set.discard(agent)

    def append(self, value):
        """
        Append a single value to the end of the
        stream.
        """
        if self.closed:
            raise Exception("Cannot write to a closed stream.")
        self.recent[self.stop] = value
        self.stop += 1
        # Inform subscribers that the stream has been
        # modified.
        for a in self.subscribers_set:
            a.next()

        # Manage the list recent.
        # Set up a new version of the list
        # (if necessary) to prevent the list
        # from getting too long.
        self._set_up_new_recent()

    def extend(self, value_list):
        """
        Extend the stream by the list of values, value_list.

        Parameters
        ----------
            value_list: list
        """
        if self.closed:
            raise Exception("Cannot write to a closed stream.")

        assert (isinstance(value_list, list) or
                isinstance(value_list, np.ndarray))

        # Since this stream is a regular Stream (i.e.
        # implemented as a list) rather than Stream_Array
        # (which is implemented as a NumPy array), convert
        # any NumPy arrays to lists before inserting them
        # into the stream. See StreamArray for dealing with
        # streams implemented as NumPy arrays.
        if isinstance(value_list, np.ndarray):
            value_list = value_list.tolist()

        if len(value_list) == 0:
            return

        if isinstance(value_list, list):
            if _close in value_list:
                # Since _close is in value_list, first output
                # the messages in value_list up to the message
                # _close and then close the stream.
                # close_flag indicates that this stream must
                # be closed after earlier messages in value_list
                # are output.
                close_flag = True
                index_of_close = value_list[_close]
                value_list = value_list[:index_of_close]
            else:
                close_flag = False

        self.new_stop = self.stop + len(value_list)
        self.recent[self.stop: self.new_stop] = value_list
        self.stop = self.new_stop
        # Inform subscribers that the stream has been
        # modified.
        for a in self.subscribers_set:
            a.next()

        # Manage the list recent in the same way as done
        # for the append() method.
        self._set_up_new_recent()

        # Close the stream if close_flag was set to True
        # because a _close value was added to the stream.
        if close_flag:
            self.close()

    def set_name(self, name):
        self.name = name

    def print_recent(self):
        print self.name, '=', self.recent[:self.stop]

    def close(self):
        """
        Close this stream."
        """
        if self.closed:
            return
        print "Stream " + self.name + " in " + self.proc_name + " closed"
        self.closed = True
        # signal subscribers that the stream has closed.
        # for a in self.subscribers_set: a.signal()

    def set_start(self, reader, start):
        """ The reader tells the stream that it is only accessing
        elements of the list recent with index start or higher.

        """
        self.start[reader] = start

    def _set_up_new_recent(self):
        """
        Implement a form of garbage collection for streams
        by updating the list recent to delete elements of
        the list that are not accessed by any reader.
        """
        # _begin = 0 if start is the empty dict,
        # else _begin = min over all r of start[r]
        self._begin = (0 if self.start == {}
                       else min(self.start.itervalues()))
        # If stop < len(recent) - _buffer_size then recent has
        # enough empty slots to add the values appended to
        # the stream; so no need to change recent.
        if self.stop < len(self.recent) - self._buffer_size:
            return

        # recent does not have enough empty slots for the
        # new values appended to the stream. So, create a
        # new recent.
        # If some reader is slow compared to the rate at which
        # values are appended to the stream, then _begin is
        # small compared to _buffer_size. On the other hand, if
        # all readers are moving the windows that they read
        # forward as fast as values are appended to the stream
        # then _begin will be large, almost equal to len(recent).
        # If some reader is very slow, then double the size of
        # recent and then double _buffer_size
        if self._begin > self._buffer_size:
            # All readers are keeping up with the stream
            new_size = len(self.recent)
            # Do not change _buffer_size
        else:
            new_size = len(self.recent) * 2
            self._buffer_size *= 2
        # 0 is the padding value.
        self.new_recent = [0] * new_size

        # Copy the values that readers can read, and ONLY those
        # values into new_recent. Readers do not read values in
        # recent with indexes smaller than _begin, and recent has
        # no values with indexes greater than stop.
        self.new_recent[:self.stop - self._begin] = \
            self.recent[self._begin: self.stop]
        self.recent, self.new_recent = self.new_recent, self.recent
        del self.new_recent
        # Maintain the invariant recent[i] = stream[i + offset]
        # by incrementing offset since messages in new_recent were
        # shifted left (earlier) from the old recent by offset
        # number of slots.
        self.offset += self._begin
        # A reader reading the value in slot l in the old recent
        # will now read the same value in slot (l - _begin) in
        # new_recent.
        for key in self.start.iterkeys():
            self.start[key] -= self._begin
        self.stop -= self._begin
        self._begin = 0

    # def _create_recent(self, size): return [0] * size


##########################################################
class StreamArray(Stream):
    def __init__(self, name=None):
        super(StreamArray, self).__init__(name)

    def _create_recent(self, size): return np.zeros(size)

    def extend(self, a):
        """
        Extend the stream by an numpy ndarray.

        Parameters
        ----------
            a: np.ndarray or list
        """
        if self.closed:
            raise Exception("Cannot write to a closed stream.")

        if isinstance(a, list):
            a = np.array(a)
        assert isinstance(a, np.ndarray),\
            "Expect extension of a numpy stream to be a numpy ndarray,\
            not '{0}' ".format(a)

        if len(a) == 0:
            return

        self.new_stop = self.stop + len(a)
        self.recent[self.stop: self.new_stop] = a
        self.stop = self.new_stop
        # Inform subscribers that the stream has been
        # modified.
        for subscriber in self.subscribers_set:
            subscriber.next()

        # Manage the array 'recent' in the same way as done
        # for the append() method.
        self._set_up_new_recent()


class StreamSeries(Stream):
    def __init__(self, name=None):
        super(StreamSeries, self).__init__(name)

    def _create_recent(self, size): return pd.Series([np.nan] * size)


class StreamTimed(Stream):
    def __init__(self, name=None):
        super(StreamTimed, self).__init__(name)

    def _create_recent(self, size):
        return [TimeAndValue(v, 0) for v in range(size)]
