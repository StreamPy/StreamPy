""" This module contains the Stream class. The
Stream and Agent classes are the building blocks
of PythonStreams.
"""

from SystemParameters import DEFAULT_STREAM_SIZE, DEFAULT_BUFFER_SIZE_FOR_STREAM
# Import numpy and pandas if StreamArray (numpy) and StreamSeries (Pandas)
# are used.
import numpy as np
#import pandas as pd
from collections import namedtuple

TimeAndValue = namedtuple('TimeAndValue', ['time', 'value'])
_no_value = object

class _multivalue(object):
    def __init__(self, lst):
        self.lst = lst
        

class Stream(object):
    """
    A stream is a sequence of values. Agents can:
    (1) Append values to the tail of stream. 
    (2) Read a stream.
    (3) Subscribe to be notified when a
    value is added to a stream.

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
    a writer of the same stream.

    If agent x is a subscriber to a stream s then
    x.next() --- a state transition of x --- is
    invoked whenever s is modified.

    READING A STREAM
    An agent can read a stream only after it registers
    with the stream as a reader. An agents r registers
    with a stream s by executing s.reader(r).
    
    After a reader of a stream s reads the first k
    values s, the reader may determine that from that
    point onwards, it will no longer read the
    first j values of the stream for some j where
    j <= k.
    A reader r of a stream s can inform s at a point
    in the computation that from that point onwards
    r will no longer read the first j values of the
    stream, for some j. Stream s uses this information
    to manage its memory.

    Associated with each stream s is a list s.recent
    which consists of the most recent elements of s.
    s.recent is a tailing subsequence (or suffix) of
    s.
    If the value of s is a sequence s[0], ..., s[n-1],
    at a point in a computation then at that point,
    s.recent is a list s[m], .., s[n-1] for some m.
    
    The length of s.recent is large enough so that at
    each point in a computation, all readers of stream
    s only read elements of s that are in s.recent. 
    Operations on streams are implemented as operations
    on lists. A reader reads a stream s by reading the
    list s.recent.

    Associated with a reader r of stream s is an
    integer s.start[r]. Reader r can only read the slice
    s.recent[s.start[r] : ] of the list recent.
    Reader r informs stream s that it will only
    read values in the list recent with indexes
    greater than or equal to j by calling
         s.set_start(r, j)
    which causes s.start[r] to be set to j.
    
    For readers r1 and r2 of a stream s the values
    s.start[r1] and s.start[r2] may be different.

    WRITING A STREAM
    An agent adds elements to a stream s by calling
    s.append(value) or s.extend(value_list); these
    operations are similar to operations on lists.
    s.append(value) appends the single value to the
    tail of the list and s.extend(value_list) extends
    the stream by the sequence of values in the list
    value_list.

    SUBSCRIBE TO BE CALLED WHEN A STREAM IS MODIFIED
    An agent x subscribes to a stream s by executing
            s.call(x).
    Then, when stream s is modified, s calls x.next(s)
    where next() executes a state-transition.
    An agent x unsubscribe from a stream s by executing
            s.delete_caller(x)

    CLOSING A STREAM
    A stream can be closed or open (i.e., not closed).
    Initially a stream is open. The agent that writes a
    stream s can close s by executing s.close().
    A closed stream cannot be modified.
    
    Associated with a stream s is:
    (1) a list, s.recent. 
    (2) a nonnegative integer s.stop  where:
      (a) the slice s.recent[:s.stop] contains
      the most recent values of stream s, and
      (b) the slice s.recent[s.stop:] is
      padded with padding values (either 0 or 0.0).
    (3) a nonnegative integer s.offset where
          recent[i] = stream[i + offset]
             for 0 <= i < s.stop
    For example, if the stream s consists of range(950),
    i.e., 0, 1, .., 949, and s.offset is 900, then
    s.recent[i] = s[900+i] for i in range(50).

    Note that the number of entries in stream s is:
    s.offset + s.stop

    Parameters
    ----------
    name: str (optional)
          name of the stream. Though the name is optional
          a named stream helps with debugging.
    
    Attributes
    ----------
    recent: list
          A list of the most recent values of the stream.
    stop:   index into the list recent.
          s.recent[:s.stop] contains the s.stop most recent
          values of stream s.
          s.recent[s.stop:] contains padded values.
    offset: index into the stream.
          For a stream s:
          s.recent[i] = s[i + offset] for i in range(s.stop)
    start: dict of readers.
             key = reader
             value = start index of the reader
             Reader r can read the slide recent[start[r] : ]
    subscribers_set: set
             the set of subscribers for this stream, agents to be notified when an
             element is added to the stream.
    closed: boolean
             True if and only if the stream is closed.
             A closed stream is not modified.
    _buffer_size: nonnegative integer
            Used to manage the recent list.
    _begin: index into the list recent
            recent[_begin:] mqy be read by some reader.
            recent[:_begin] is not being accessed by any reader;
            therefore recent[:_begin] can be safely deleted.

    """
    def __init__(self, name="No Name", proc_name="Unkown Process"):
        self.name = name
        # Name of the process in which this stream lives.
        self.proc_name = proc_name
        # Create the list recent and the parameters
        # associated with garbage collecting
        # elements in the list.
        self.recent = self._create_recent(DEFAULT_STREAM_SIZE)
        self._buffer_size = DEFAULT_BUFFER_SIZE_FOR_STREAM
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

    def reader(self, reader, start=0):
        """
        Register a reader.

        The newly registered reader starts reading list recent
        from index start, i.e., reads the slice
        recent[start:s.stop]
        If reader has already been registered with this stream
        its start value is updated to the parameter in the call.
        """
        self.start[reader] = start

    def delete_reader(self, reader):
        """
        Delete this reader from this stream.
        """
        if reader in start: del start[reader]

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
        ## if value == _no_value:
        ##     return
        if self.closed:
            raise Exception("Cannot write to a closed stream.")
        self.recent[self.stop] = value
        self.stop += 1
        # Inform subscribers that the stream has been
        # modified.
        for a in self.subscribers_set: a.next()
                            
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
        
        assert isinstance(value_list, list) or isinstance(value_list, np.ndarray) ,\
          "Expect extension of a stream to be a list or array, not '{0}' ".format(value_list)

        if isinstance(value_list, np.ndarray):
            value_list = value_list.tolist()

        ## value_list = [v for v in value_list if v != _no_value]
        
        if len(value_list) == 0:
            return

        self.new_stop = self.stop + len(value_list)
        self.recent[self.stop : self.new_stop] = value_list
        self.stop = self.new_stop
        # Inform subscribers that the stream has been
        # modified.
        for a in self.subscribers_set: a.next()

        # Manage the list recent in the same way as done
        # for the append() method.
        self._set_up_new_recent()

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
        #for a in self.subscribers_set: a.signal()
        
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
        self._begin = 0 if self.start == {} else min(self.start.itervalues())
        if self.stop < len(self.recent) - self._buffer_size: return
        self.new_recent = self._create_recent(
            len(self.recent) * (1 if self._begin > self._buffer_size else 2))
        self.new_recent[:self.stop - self._begin] = \
          self.recent[self._begin : self.stop]
        self.recent, self.new_recent = self.new_recent, self.recent
        del self.new_recent
        self.offset += self._begin
        for key in self.start.iterkeys():
            self.start[key] -=  self._begin
        self.stop -= self._begin
        self._begin = 0


    def _create_recent(self, size): return [0] * size


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
          "Expect extension of a numpy stream to be a numpy ndarray, not '{0}' ".format(a)
        
        if len(a) == 0:
            return

        self.new_stop = self.stop + len(a)
        self.recent[self.stop : self.new_stop] = a
        self.stop = self.new_stop
        # Inform subscribers that the stream has been
        # modified.
        for subscriber in self.subscribers_set: subscriber.next()

        # Manage the array 'recent' in the same way as done
        # for the append() method.
        self._set_up_new_recent()



        

class StreamSeries(Stream):
    def __init__(self, name=None):
        super(StreamSeries, self).__init__(name)

    def _create_recent(self, size): return pd.Series([np.nan] *size)

class StreamTimed(Stream):
    def __init__(self, name=None):
        super(StreamTimed, self).__init__(name)

    def _create_recent(self, size):
        return [TimeAndValue(v, 0) for v in range(size)]

    
        
