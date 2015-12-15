""" This module contains the Agent class. The Agent
and Stream classes are the building blocks of
PythonStreams.

"""

from Stream import Stream, StreamArray, StreamSeries, StreamTimed
from collections import namedtuple
import math

# EPSILON is a small number used to prevent division by 0
# and other numerical problems
EPSILON = 1E-12

InList = namedtuple('InList', ['list', 'start', 'stop'])

class Agent(object):
    """
    An agent is an automaton: a state-transition machine.
    An agent is initialized in __init__ and a state
    transition is executed by next().

    An agent has lists of input streams, output streams
    and call streams. Streams are described in Stream.py.
    
    During a state transition an agent may read values from
    its input streams, append values to its output streams,
    change its state and carry out operations on other objects.

    When a call stream is modified the agent's next() method
    is called which causes the agent to execute a state transition.
    
    The default is that every input stream is also a call stream,
    i.e., the agent executes a state transition when any of its
    input streams is modified. For performance reasons, we
    may not want the agent to execute state transitions when some
    input streams are modified; in this case, the sets of call
    and input streams will be different.

    Named_Tuple
    ----------------
    InList : a named_tuple with arguments:
        list, start, stop
        An InList defines the list slice:
                   list[start:stop]
    
    Parameters
    ----------
    in_streams : list of streams
    out_streams : list of streams
    call_streams : list of streams
        When a new value is added to a stream in this list
        a state transition is invoked.
        This the usual way (but not the only way) in which
        state transitions occur.
    state: object
        The state of the agent. The state is updated after
        a transition.
    transition: function
        This function is called by next() which
        is the state-transition operation for this agent.
        An agent's state transition is specified by
        its transition function.
    stream_manager : function
        Each stream has management variables, such as whether
        the stream is open or closed. After a state-transition
        the agent executes the stream_manager function
        to modify the management variables of the agent's output
        and call streams.
    name : str, optional
        name of this agent

    Attributes
    ----------
    _in_lists: list of InList
        InList defines the slice of a list.
        The j-th element of _in_lists is an InList
        that defines the slice of the j-th input stream
        that may be read by this agent in a state
        transition.
              
    _out_lists: list
        The j-th element of the list is the list of
        values to be appended to the j-th output
        stream after the state transition.

    Methods
    -------
    next(stream_name=None)
        Execute a state transition. The method has 3 parts:
           (i) set up the data structures to execute
               a state transition,
           (ii) call transition to:
                (a) get the values to be appended to output streams,
                (b) get the next state, and
                (c) update pointers into input streams identifying what
                    parts of the stream may be read in the future.
           (iii) update data structures after the transition.

    """

    def __init__(self, in_streams, out_streams, transition,
                 state=None, call_streams=None,
                 stream_manager=None, name=None):
        self.in_streams = in_streams
        self.out_streams = out_streams
        self.state = state
        self.transition = transition
        # The default is that the agent executes a state
        # transition when any of its input streams is modified.
        self.call_streams = in_streams if call_streams is None \
          else call_streams
        self.stream_manager = stream_manager
        self.name = name
        # Register this agent as a reader of its input streams.
        if self.in_streams is None:
            # A source. Make in_streams and empty list.
            self.in_streams = []
        for s in self.in_streams:
            s.reader(self)
        # Register this agent to be called when any of its call
        # streams is extended.
        for s in self.call_streams:
            s.call(self)
        # Initially each element of in_lists is the
        # empty InList: list = [], start=stop=0
        self._in_lists = [InList([], 0, 0) for s in self.in_streams]
        self._in_lists_start_values = [0 for s in self.in_streams]
        # Initially each element of _out_lists is the empty list.
        self._out_lists = [[] for s in self.out_streams]
        ###############################
        self.next()

    def next(self, stream_name=None):
        """Execute the next state transition.

        This function does the following:
        Part 1: set up data structures for the state transition.
        Part 2: execute the state transition by calling self.transition
        Part 3: update data structures after the transition.

        This method can be called by any agent and is
        called whenever a value is appended to any
        stream in call_streams

        Parameters
        ----------
        stream_name : str, optional
            A new value was appended to the stream with name
            stream_name as a result of which this agent
            executes a state transition.

        """
        # PART 1
        # Set up data structures, _in_lists, _out_lists, for
        # the state transition.
        self._in_lists = [InList(s.recent, s.start[self], s.stop)\
                          for s in self.in_streams]
        self._out_lists = [[] for s in self.out_streams]

        # PART 2
        # Execute the transition_function
        # Compute:
        # (1) lists to extend output streams,
        #      assigned to self._out_lists
        # (2) the next state which is assigned to self.state,
        # and (3)  new values of stream.start for each stream
        # in input streams assigned to self._in_lists_start_values
        self._out_lists, self.state, self._in_lists_start_values  = \
          self.transition(self._in_lists, self.state)

        # PART 3
        # Update data structures after the state transition.
        # Extend output streams with new values generated in the
        # state transition.
        if self._out_lists is None:
            # Only in the case of a sink!
            # Make out_lists a list of length 0
            self._out_lists = []
        if len(self._out_lists) != len(self.out_streams):
            raise ValueError(
                'number of output lists, {0}, not equal to number of output streams, {1}'.\
                format(len(self._out_lists),len(self.out_streams)))
        for j in range(len(self.out_streams)):
            self.out_streams[j].extend(self._out_lists[j])
        # Inform streams that the agent will no longer read some of
        # the earlier elements of the input streams by updating start
        # indexes for the input streams to new values
        # (_in_lists[key].start).
        for j in range(len(self.in_streams)):
            self.in_streams[j].set_start(self, self._in_lists_start_values[j])
        # Update stream management variables. 
        if self.stream_manager is not None:
            self.stream_manager(self.out_streams,
                                       self._in_lists, self._out_lists, self.state)
