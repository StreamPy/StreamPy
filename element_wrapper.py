"""This module contains examples of the 'element' wrapper.
A function that takes a single element of an input stream
and generates a single element of an output stream is an
example of a function that is wrapped by the 'element'
wrapper to create a function on streams.

The module has the following parts:
(1) op or simple operator:
        single input, single output
(2) sink:
        single input, no outputs
(3) source:
        no input, multiple outputs
(4) split:
        single input, multiple output
(5) merge:
        multiple input, single output
(6) general case:
        multiple input, multiple output

All of the first 5 cases are specializations of
the general case; however, the syntactic sugar they
provide can be helpful.

For each of the above cases we first consider agents
that are stateless and then consider agents with state.

"""
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream, _no_value
from Operators import stream_func

#######################################################
#            PART 1
#   SINGLE INPUT, SINGLE OUTPUT.
#######################################################

#______________________________________________________
# PART 1A: Stateless
# Single input, single output, stateless functions

# Inputs to the functions:
#  element : object
#            element of the input stream

# Returned by the functions:
# element : object
#           element to be placed on the output stream.
#______________________________________________________


#            EXAMPLE 1
#
# SPECIFICATION:
# Write a function, square_stream, that has a single 
# input stream and that returns a stream whose elements
# are the squares of the elements of its input
# stream.

# If y = square_stream(x)
# and x is a stream with initial values [1, 3, 5, ...] then
# y must be a stream with initial values [1, 9, 25, ...]
# See main()
#
# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that returns squares of
# its single input value.
def square(v): return v*v

# Second step:
# Wrap the above function, square, using wrapping
# function stream_func to obtain the desired
# function square_stream.
def square_stream(stream):
    return stream_func(
        inputs=stream, f_type='element', f=square, num_outputs=1)

# stream_func is the wrapper.
# f_type specifies how the function f is to be wrapped.
# The initial examples have f_type='element' which
# assumes that f operates on single elements of input streams
# and produces single elements of output streams.
# num_outputs is the number of output streams. We begin
# with examples in which num_outputs=1.
# inputs is set to the parameter of square_stream, and
# so inputs=stream.
# In this initial set of examples, the function has
# a single input stream. So inputs is the parameter

# You can also obtain a stream y1 that squares elements of
# a stream x using stream_func directly, without defining
# the function square_stream first:
# y1 = stream_func(
#      inputs=x, f_type='element', f=square, num_outputs=1)
# See main()

#
#          EXAMPLE 2
#
# SPECIFICATION:
# Write a function, double_stream, that has a single 
# input stream and that returns a stream whose elements
# are twice the values of the elements of its input
# stream.
#
# If z = double_stream(x)
# and x is a stream with initial values [1, 3, 5, ...]
# then z must be a stream with initial values [2, 6, 10, ...]
# See main()
#
# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function double that returns the double of
# its single input value.
def double(v): return 2*v

# Second step:
# Wrap the above function, double, to obtain
# the desired function double_stream.
def double_stream(stream):
    return stream_func(
        inputs=stream, f_type='element', f=double, num_outputs=1)

# We could also have obtained the desired stream z1
# using stream_func directly,
z1 = stream_func(
    inputs=x, f_type='element', f=double, num_outputs=1)



#          EXAMPLE 3
# Example of function composition.
# Generate a stream w that doubles the squares of the elements
# of stream x
w = double_stream(square_stream(x))
# If x is a stream [1, 3, 5, ...] then
# w is a stream [2, 18, 50, ...]
#
# Generate a stream w2 that squares twice the elements
# of stream x
w2 = square_stream(double_stream(x))
# If x is a stream [1, 3, 5, ...] then
# w2 is a stream [4, 36, 100, ...]


#          EXAMPLE 4
# Illustrating use of _no_value.

# SPECIFICATION:
# Write a function, discard_odds, that has a single 
# input stream and that returns a single stream whose elements
# are the same as its input stream except that odd
# numbers are discarded.
#
# If v = discard_odds(x)
# and x is a stream [1, 2, 3, 4, 5, 6, ...] then
# v must be the stream [2, 4, 6,.....]
#
# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function with a single input that returns
# its single input value if the input value is even
# and returns _no_value otherwise.
def even(v):
    if not v%2: return v
    else: return _no_value
#
# _no_value is a special object that is not placed
# in an output stream.
#
# Second step:
# Wrap the above function, even, to obtain
# the desired function discard_odds.
def discard_odds(stream):
    return stream_func(
        inputs=stream, f_type='element', f=even, num_outputs=1)

# Explanation of need for _no_value
#
# Consider the following example that returns None rather than
# _no_value for odd numbers.
def even_1(v):
    if not v%2: return v
    else: return None

def discard_odds_1(stream):
    return stream_func(
        inputs=stream, f_type='element', f=even_1, num_outputs=1)
#
# If v_1 = discard_odds_1(x) and
# x is a stream [1, 2, 3, 4, ...] then
# v_1 is a stream[None, 2 None, 4, ...] which is not the
# same as [2, 4, ...]


#          EXAMPLE 5
# Illustrating use of _multivalue.
# If Python function f returns _multivalue(l)
# where l is a list then the agent appends each
# element of l to the agent's output stream.
# For example, if f returns _multivalue([3, 4])
# then 3 and then 4 will be appended to the
# agent's output stream.
# Note that if f returns [3, 4] then the list
# [3, 4] will be appended to the agent's output
# stream; this is not the same as appending 3 and
# then 4.

# SPECIFICATION:
# Write a function evens_and_halves with a single
# input stream that returns a single stream in
# which odd values in the input stream are discarded
# and even values and half their values appear in
# the output stream.
#
# If u = evens_and_halves(x) and
# x is a stream [1, 2, 3, 4, 5, 6, ..] then
# u must be the stream [2, 1, 4, 2, 6, 3,  .....]

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function with a single input v and that
# returns _multivalue([v, v/2] if v is even
# and returns _no_value otherwise.
def even2(v):
    if not v%2: return _multivalue([v, v/2])
    else: return _no_value
        
# Second step:
# Wrap the above function, even2, to obtain
# the desired function evens_and_halves.
def evens_and_halves(stream):
    return stream_func(
        inputs=stream, f_type='element', f=even2, num_outputs=1)

# Illustration of the need for _multivalue
# As a contrast to even2 consider the following:
def even3(v):
    if not v%2: return [v, v/2]
    else: return _no_value
        
def evens_and_halves_3(stream):
    return stream_func(
        inputs=stream, f_type='element', f=even3, num_outputs=1)

# If t = evens_and_halves_3(x)
# and x is a stream [1, 2, 3, 4, 5, 6, ..] then
# t is the stream [[2, 1], [4, 2], [6, 3],  .....] which is
# different fro [2, 1, 4, 2, 6, 3, ...]



#          EXAMPLE 6
# Illustrating use of local variables.

# SPECIFICATION:
# Write a function multiply_elements_in_stream
# with two input parameters:
# (1) stream: a stream of numbers and
# (2) multiplier: a number
# The function returns a single stream whose
# elements are multiplier times the corresponding
# elements of the input stream.

# If s = multiply_elements_in_stream(stream=x, multiplier=3)
# and x is a stream [1, 2, 3, 4, ...] then
# s must be the stream [3, 6, 9, 12,...]

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function mult(v) that returns multiplier times
# v, where multiplier is a constant specified outside
# mult.
# def mult(v): return multiplier*v

# Second step:
# Wrap the function, mult, to obtain
# the desired function multiply_elements_in_stream.
# Define mult inside the definition of
# multiply_elements_in_stream so that the parameter
# multiplier is available to function mult.
def multiply_elements_in_stream(stream, multiplier):
    def mult(v): return multiplier*v
    return stream_func(
        inputs=stream, f_type='element', f=mult, num_outputs=1)


#          EXAMPLE 7
# Another example illustrating use of local variables.

# SPECIFICATION:
# Write a function boolean_of_values_greater_than_threshold
# with two input parameters:
# (1) stream: a stream of numbers and
# (2) threshold: a number
# The function returns a single stream whose
# elements are True if the corresponding
# elements of the input stream exceed threshold and
# are False otherwise.

# If
# r = boolean_of_values_greater_than_threshold(stream=x, threshold=4)
# and x is a stream [1, 20, 31, 4, ...] then
# r must be the stream [False, True, True, False,...]



# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function value_greater_than_threshold(value)
# that returns True if value exceed threshold
# where threshold is a constant specified outside
# value_greater_than_threshold.
# def value_greater_than_threshold(value):
#        return value > threshold

# Second step:
# Wrap the function, value_greater_than_threshold, to
# obtain the desired function,
#   boolean_of_values_greater_than_threshold.
# Define value_greater_than_threshold inside the definition
# of boolean_of_values_greater_than_threshold so that the
# parameter threshold is available to function
# boolean_of_values_greater_than_threshold.

def boolean_of_values_greater_than_threshold(stream, threshold):
    def value_greater_than_threshold(value):
        return value > threshold
    return stream_func(
        inputs=stream, f_type='element',
        f=value_greater_than_threshold, num_outputs=1)



#______________________________________________________
# PART 1B
# Single input, single output, stateful functions

# Inputs to the functions:
# element : object
#            element of the input stream
# state : state of the agent before the transition

# Returned by the functions:
# element : object
#           element to be placed on the output stream.
# state : object
#         The next state of the agent.
#
# The form of the wrapper in these examples is:
# stream_func(
#     inputs=stream, # The name of the input stream
#     f_type='element',
#     f=g, # The name of the function that is wrapped
#     num_outputs=1 # The number of outputs
#     )

#______________________________________________________

#          EXAMPLE 1
# An example illustrating state.

# SPECIFICATION:
# Write a function cumulative_stream with a single
# input stream and that returns a single stream where
# the j-th element of the output stream is the sum
# of the first j elements of its input stream.

# If b = cumulative_stream(stream=x)
# and x is a stream [1, 2, 3, 4, ...] then
# b must be the stream [1, 3, 6, 10, ....]

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function cumulative_sum given below.

def cumulative_sum(v, cumulative):
    """
    Parameters
    ----------
    v : number
       The next element of the input stream of the
       agent.
    cumulative: number
       The state of the agent. The state is the sum
       of all the values received on the agent's
       input stream.

    Returns
    -------
    (cumulative, cumulative)
    cumulative : number
       The state after the transition, i.e., the
       sum of values received on the agent's input
       stream including the value received in this
       transition.

    """
    cumulative += v
    return (cumulative, cumulative)

# Second step:
# Wrap the function, cumulative_sum, to
# obtain the desired function, cumulative_stream.
# Since the function has state, the wrapper specifies
# the initial state: state=0.
def cumulative_stream(stream):
    return stream_func(
        inputs=stream,
        f_type='element',
        f=cumulative_sum,
        num_outputs=1,
        state=0 # The initial state
        )
 


#          EXAMPLE 2
# Another  example illustrating state.

# SPECIFICATION:
# Write a function average_stream that has a
# single input stream and returns a stream where
# the j-th element of the output stream is the average
# of the first j elements of its input stream.

# If c = cumulative_stream(stream=x)
# and x is a stream [1, 2, 3, 4, ...] then
# c must be the stream [1.0, 1.5, 2.0, 2.5, ....]

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function average given below.

def average(v, state):
    """
    Parameters
    ----------
    v : number
       The next element of the input stream of the
       agent.
    state: (n, cumulative)
       The state of the agent where
       n : number
           The value of the next element in the agent's
           input stream.
       cumulative : number
           The sum of the values that the agent has
           received on its input stream.

    Returns
    -------
    (mean, state)
    mean : floating point number
       The average of the values received so far by
       the agent
    state : (n, cumulative)
       The new state of the agent.

    """
    n, cumulative = state
    n += 1
    cumulative += v
    mean = cumulative/float(n)
    state = (n, cumulative)
    return (mean, state)

# Second step:
# Wrap the function, average, to
# obtain the desired function, average_stream.
# Since this function has a state, the wrapper
# specifies the initial state: state=(0,0.0).
def average_stream(stream):
    return stream_func(
        inputs=stream,
        f_type='element',
        f=average,
        num_outputs=1,
        state=(0, 0.0) # The initial state
        # Initially n = 0, cumulative = 0.0
        )
 


#######################################################
#            PART 2: SINKS
#      SINGLE INPUT, NO OUTPUT.
#######################################################

#______________________________________________________
# PART 2A: Stateless
# Single input, no output, stateless functions

# Inputs to the functions:
#  element : object
#            element of the input stream
# Returned by the functions:
#             None
#
# The form of the wrapper in these examples is:
# stream_func(
#     inputs=stream, # The name of the input stream
#     f_type='element',
#     f=g, # The name of the function that is wrapped
#     num_outputs=0 # The number of outputs
#     )

#______________________________________________________


#          EXAMPLE 1

# SPECIFICATION:
# Write a function print0 that has a single input
# stream and that returns None. The function
# prints the values of its input stream.
# If the input stream has initial values [3, 5, ...]
# and the stream name is 'x' then the function should
# print:
# x : 3
# x : 5

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function p0 with a single parameter, v, where
# p0 prints the name of a stream (specified outside p0)
# and the value of v.
# def p0(v):
#    print '{0} : {1}'.format(stream.name, v)

# Second step:
# Wrap the function, p0, to obtain the desired function,
# print0. Define p0 inside the definition
# of print0 so that p0 can access the parameter,
# stream of print0.
# This function doesn't have to keep track of its past,
# and so it has no state. Therefore, the wrapper
# stream_func does not specify a state.
def print0(stream):
    def p0(v):
        print '{0} : {1}'.format(stream.name, v)
    return stream_func(
        inputs=stream, f_type='element',
        f=p0, num_outputs=0)


#          EXAMPLE 2
# Illustrates state.

# SPECIFICATION:
# Write a function print_stream that has a single input
# stream and that returns None. The function
# prints the values with the indexes of its input stream.
# If the input stream has initial values [3, 5, ...]
# and the stream name is 'x' then the function should
# print:
# x[0] = 3
# x[1] = 5

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# The function has to keep track of the number of values
# that have already been printed; so we need a state.
# Write a function print_element with two parameters, v,
# the value in a stream, and count --- the number of elements
# printed so far. The function returns the new state, i.e.,
# the new value of count. The function uses a variable stream
# specified outside the function.
#def print_element(v, count):
#    print '{0}[{1}] = {2}'.format(stream.name, count, v)
#        return (count+1)

# Second step:
# Wrap the function, print_element, to obtain the desired function,
# print_stream. Define print_element inside the definition
# of print_stream so that print_element can access the parameter,
# stream of print_stream.
# This function has a state, namely count, and so the wrapper
# specifies its initial value: 'state=0'.

def print_stream(stream):

    def print_element(v, count):
        print '{0}[{1}] = {2}'.format(stream.name, count, v)
        return (count+1)

    return stream_func(
        inputs=stream, f_type='element',
        f=print_element, num_outputs=0,
        state=0)




#######################################################
#            PART 3: SOURCES
#      NO INPUTS, ONE OR MORE OUTPUTS.
#######################################################

#______________________________________________________
# PART 3A: Stateless
# No inputs, one or more outputs, stateless functions
# Illustrates the use of call_streams and illustrates
# that append and extend of a stream are analogous to
# the same operations on lists.
#______________________________________________________

#          EXAMPLE 1

# SPECIFICATION:
# Write a function, timer, with three parameters:
# s, N and T where s is a stream, N is a
# positive integer and T is a positive
# number.
# The function generates a stream consisting
# of the values [0, 1,..., N-1]. An integer
# is output to the stream every T seconds.

# THE STREAMING PROGRAM.
# Illustrates that s.append(i) is analogous
# to l.append(i) where s is a stream and l
# is a list.
import time
def timer(s, N, T):
    """
    Parameters
    ----------
    s: Stream
    N: int, positive
    T: int or float, positive

    """
    for i in range(N):
        s.append(i)
        time.sleep(T)

        

#          EXAMPLE 2

# SPECIFICATION:
# Write a function, rand, with
# three parameters: s, N and T where
# s is a stream, N is a positive integer
# and T is a positive number.
# The function generates a stream of
# N random numbers. A random number
# is appended to the stream every T seconds.

# THE STREAMING PROGRAM.
import time
import random
def rand(s, N, T):
    """
    Parameters
    ----------
    s: Stream
    N: int, positive
    T: int or float, positive

    """
    for _ in range(N):
        s.append(random.random())
        time.sleep(T)


#          EXAMPLE 3

# SPECIFICATION:
# Write a function, file_to_stream, with
# three parameters: filename, a stream
# and a time interval.
# The function has access to a file:
# filename.txt
# The function outputs a line of the
# file to the stream every T seconds.

# THE STREAMING PROGRAM.
import time
def file_to_stream(filename, stream, T):
    """
    Parameters
    ----------
    filename: str
    stream: Stream
    T: int or float, positive

    """
    with open('filename.txt') as fp:
        for line in fp:
            s.append(line)
            time.sleep(T)


#          EXAMPLE 4

# Illustrates the use of call_streams

# SPECIFICATION:
# Write a function, random_stream, analogous
# to the function in example 2 (rand) except that
# a step is taken (i.e. a value is appended to the
# output stream) when a timer_stream is
# modified. The timer_stream is specified outside
# the function random_stream. random_stream returns
# a stream: the stream of random numbers.
# Note that in function, rand, the stream is passed
# to rand as a parameter; by contrast, the stream
# is not passed to the function, random_stream, 
# which creates and returns the stream.

# Note that in the wrapper, stream_func, the
# parameter call_streams is a LIST of streams, and
# so, the correct code is:
#        call_streams=[timer_stream]
# not:
#         call_streams=timer_stream

# THE STREAMING PROGRAM.
def single_stream_of_random_numbers(timer_stream):
    return stream_func(
        inputs=None,
        f_type='element',
        f=random.random,
        num_outputs=1,
        call_streams=[timer_stream])


 
if __name__ == '__main__':
    main()

