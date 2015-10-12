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
## Commenting this section that appends everything on the path
## if __name__ == '__main__':
##     if __package__ is None:
##         import sys
##         from os import path
##         sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from Stream import Stream, _no_value, _multivalue
from Operators import stream_func
import json
import numpy as np

#######################################################
#            PART 1
#   SINGLE INPUT STREAM, SINGLE OUTPUT STREAM.
#######################################################

#______________________________________________________
# PART 1A: Stateless
#______________________________________________________
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
# z1 = stream_func(
#    inputs=x, f_type='element', f=double, num_outputs=1)



#          EXAMPLE 3
# Example of function composition.
# Generate a stream w1 that doubles the squares of the elements
# of stream x
# w1 = double_stream(square_stream(x))
# If x is a stream [1, 3, 5, ...] then
# w1 is a stream [2, 18, 50, ...]
#
# Generate a stream w2 that squares twice the elements
# of stream x
# w2 = square_stream(double_stream(x))
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
# different from [2, 1, 4, 2, 6, 3, ...]



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
#______________________________________________________
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
#     num_outputs=1, # The number of outputs
#     state=initial_state # specifies the initial state
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
#      SINGLE INPUT STREAM, NO OUTPUT STREAMS.
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


#          EXAMPLE 3

# SPECIFICATION:
# Write a function stream_to_file that has two
# parameters, a single input stream and a filename.
# The function returns None. The function
# appends the json representations of the values
# of its input stream into the file with name filename.

# If the input stream has initial values [3, 5, ...]
# and file is initially empty then the file should
# have the json representations of 3 and 5, each on a
# separate line.
# (Note that if the file is not initially empty, then
# the stream values are appended to the end of the
# nonempty file.)

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function write_value_to_file(v) that
# appends the json representation of v to the
# file with name filename with each append on
# a new line.

# Second step:
# Wrap the function, write_value_to_file, to
# obtain the desired function, stream_to_file.
# Define write_value_to_file inside the definition
# of stream_to_file so that stream_to_file can
# access the parameter, filename.

def stream_to_file(stream, filename):
    def write_value_to_file(v):
        with open(filename, 'a') as input_file:
            input_file.write(json.dumps(v) + '\n')
    return stream_func(
        inputs=stream, f_type='element',
        f=write_value_to_file, num_outputs=0)



#######################################################
#            PART 3: SOURCES
#   NO INPUT STREAMS, ONE OR MORE OUTPUT STREAMS
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
# output_stream, num_outputs and time_period where
# stream is a Stream, num_outputs is a positive integer
#  and time_period is a positive number.
# 
# The function generates a stream consisting
# of the values [0, 1,..., num_outputs-1]. An integer
# is output to the stream every time_period seconds.

# THE STREAMING PROGRAM.
# Illustrates that stream.append(i) is analogous
# to l.append(i) where stream is a Stream and l
# is a list.
import time
def timer(output_stream, num_outputs, time_period):
    """
    Parameters
    ----------
    stream: Stream
    num_outputs: int, positive
    time_period: int or float, positive

    """
    for i in range(num_outputs):
        output_stream.append(i)
        time.sleep(time_period)

        

#          EXAMPLE 2

# SPECIFICATION:
# Write a function, rand, with three parameters:
# output_stream, num_outputs, time_period.
# where output_stream is a stream, num_outputs is
# a nonnegative number and time_period is an
# optional positive number. 
# The function generates a stream of
# num_outputs random numbers. If time_period
# is provided, a random number is appended
# to the stream periodically with the period
# time_period. If time_period is not provided
# random numbers are appended to the stream
# continuously.

# THE STREAMING PROGRAM.
import time
import random
def rand(output_stream, num_outputs, time_period=0):
    """
    Parameters
    ----------
    output_stream: Stream
    num_outputs: int, positive
    time_period: int or float, positive

    """
    if not time_period:
        for _ in range(num_outputs):
            output_stream.append(random.random())
    else:
        for _ in range(num_outputs):
            output_stream.append(random.random())
            time.sleep(time_period)


#          EXAMPLE 3

# SPECIFICATION:
# Write a function, file_to_stream, with
# three parameters: filename, output_stream
# and time_period (optional)
# The function reads a file called filename.
# The file has json representations of objects,
# with one or more representations per line.
# The function appends the objects in the file,
# to the stream. Objects from one line of the file
# are appended the stream every time_period seconds
# if time_period is specified. If time_period
# is not specified, the function appends objects
# from the file to the stream continuously.


# THE STREAMING PROGRAM.
import time
def file_to_stream(filename, output_stream, time_period=0):
    """
    Parameters
    ----------
    filename: str
    output_stream: Stream
    time_period: int or float, nonnegative

    """
    with open(filename, 'r') as output_file:
        for line in output_file:
            values = [json.loads(v) for v in line.split()]
            output_stream.extend(values)
            if time_period:
                time.sleep(time_period)


#          EXAMPLE 4

# Illustrates the use of call_streams

# SPECIFICATION:
# Write a function, single_stream_of_random_numbers,
# that returns a single stream of random numbers.
# A random number is appended to the output stream
# when the parameter timer_stream is modified.

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



#######################################################
#            PART 4: SPLIT
#      SINGLE INPUT STREAM, TWO OR MORE OUTPUT STREAMS.
#######################################################

#______________________________________________________
# PART 4A: Stateless
# Single input, two or more outputs, stateless functions
# A python function with a single input and a tuple of
# outputs is wrapped to produce a function with a single
# input stream and a list of output streams
#______________________________________________________

#          EXAMPLE 1

# SPECIFICATION:
# Write a function, square_and_double_stream, with a
# single parameter: an input stream. The function returns
# a list of two streams where the elements of the first
# output stream are squares of the elements of the input
# stream and the elements of the second output stream are
# twice those of the input stream. If the input is the
# stream [0, 1, 2, 3, ...] then the function returns a list
# of two streams the first of which is [0, 1, 4, 9, ...]
# and the second is [0, 2, 4, 6, ..]

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function, square_and_double with a single parameter,
# a number. The function returns a tuple of two values, the
# square and double of the input.
def square_and_double(m):
    return (m*m, 2*m)

# Second step:
# Wrap the function, square_and_double, to
# obtain the desired function, square_and_double_stream.
def square_and_double_stream(stream):
    return stream_func(
        inputs=stream,
        f_type='element',
        f=square_and_double,
        num_outputs=2 #Two output streams
        )


#          EXAMPLE 2

# SPECIFICATION:
# Write a function, exp_mult_div_stream, with four
# parameters: stream, exponent, multiplier, and
# divisor where the last three parameters are numbers.
# The function returns a list of three streams where
# the elements of the streams are the elements of the
# input stream raised to exponent, multiplied by
# multiplier and divided by divisor, respectively.
# If the input stream is [0, 1, 2, 3, ...] and exponent
# is 3, multiplier is 10, and divisor is 0.25 then the
# function returns a list of three streams:
# [0, 1, 8, 27, ...], [0, 10, 20, 30, ...], and
# [0, 4, 8, 12, ...]

# HOW TO DEVELOP THE STREAMING PROGRAM.

# Wrap the function (see below) exp_mult_div_number
def exp_mult_div_stream(stream, exponent, multiplier, divisor):
    def exp_mult_div_number(n):
        return [n**exponent, n*multiplier, n/divisor]
    return stream_func(inputs=stream,
                       f_type='element',
                       f=exp_mult_div_number,
                       num_outputs=3 # Returns list of 3 streams.
                       )


#          EXAMPLE 3
# Illustrates use of _no_value

# SPECIFICATION:
# Write a function, even_odd_stream, with one parameter: stream.
# The function returns a list of two streams, the first containing
# the even values of the input stream, and the second containing
# the odd values.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function, even_odd with a single parameter,
# a number. The function returns a tuple with 2 values,
# that will be inserted into the two output streams of the
# wrapped function. even_odd returns (_no_value, m) if m
# is even, because the odd stream gets no value and the even
# stream gets m. Symmetrically, even_odd returns (m, _no_value)
# if m is odd.
def even_odd(m):
    if m%2: return [_no_value, m]
    else: return [m, _no_value]

# Second step:
# Wrap the function, even_odd, to get the desired function.
def even_odd_stream(stream):
    return stream_func(inputs=stream,
                       f_type='element',
                       f=even_odd,
                       num_outputs=2 # Returns list of 2 streams.
                       )


#______________________________________________________
# PART 4B: Stateful
# Single input, two or more outputs, stateful functions
# Write a python function with two inputs --- a stream element
# and a state --- and that returns a tuple of stream 
# elements and the next state. Wrap the function to produce a
# function with a single input stream and a list of output
# streams.
#______________________________________________________

#          EXAMPLE 1

# SPECIFICATION:
# Write a function that has a single input stream where the
# elements of the stream are tuples:
#      (sensor name, time, sensor reading)
# The sensor name is either 'temperature' or 'humidity'
# The time is a positive integer. The sensor reading is
# a number where the temperature reading is greater than -274,
# and the humidity reading is non-negative.
# The function returns two output streams, one for temperature
# and one for humidity. If the temperature input stream has
# a value that is less than DELTA away from its previous output,
# where DELTA is a constant parameter, then that value is not
# placed on the output stream; if the value exceeds DELTA then
# it is placed on the output stream. Similarly for humidity data.
# The parameters of the function are the input stream and DELTA.
# The function returns a list of two output streams, one for
# temperature and the other for humidity.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# The state of the agent is the last value output on each of
# the temperature and humidity streams. The state is represented
# by a tuple of 2 numbers.
# Write a function t_and_h with two parameters:
# (1) msg: a 3-tuple (sensor_name, time, reading), and
# (2) a state (last_temperature, last_humidity)
# The function returns:
# (1) A 2-tuple representing the next outputs on the temperature
#     and humidity streams, and
# (2) the next state.
# The function reads a constant DELTA defined outside the function.

# Second step:
# Wrap the function, t_and_h, to get the desired function.
# Set the initial state to be a 2-tuple.
def temperature_and_humidity_streams(stream, DELTA):
    def t_and_h(msg, state):
        sensor_name, time, reading = msg
        index = 0 if sensor_name == 'temperature' else 1
        next_output = [_no_value, _no_value]
        next_state = state
        if abs(state[index] - reading) > DELTA:
            next_output[index] = msg
            state[index] = reading
        return (next_output, next_state)

    return stream_func(inputs=stream,
                       f_type='element',
                       f=t_and_h,
                       num_outputs=2, # Returns list of 2 streams.
                       state= [-274, -1] # Initial state
                       )    
        
        


#######################################################
#            PART 5: MERGE
#   TWO OR MORE INPUT STREAMS, SINGLE OUTPUT STREAM.
#
#######################################################

#______________________________________________________
# PART 5A: Merge Stateless
# Two or more inputs, single output, stateless functions.
# A python function with a single input which is a list
# and a single return value is wrapped to produce a
# function with a list of input streams and a single output
# stream.
#
# This merge is synchronous. The agent waits to receive
# the j-th message in each input stream and then carries out
# a computation on the list of j-th messages, one message per
# input stream. The agent only outputs m messages where m
# is the minimum number of messages in each of its input
# streams.
#
# For asynchronous merges see asynch_element.
#______________________________________________________        

#          EXAMPLE 1

# SPECIFICATION:
# Write a function, mean_stream that has a single parameter,
# a list of input streams. It returns a stream where the j-th
# value of the stream is the mean of the j-th values of
# its input streams. If the values of streams x, y, z
# are [3, 5, 8], [1, 7, 2], and [2, 3] and the input to
# the function is [x, y, z] then the output at this point
# is [2.0, 5.0], i.e. (3+1+2)/3.0 and (1+7+3)/3.0

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that takes a list of numbers as input
# and that returns its mean. np.mean() is such a function.

# Second step:
# Wrap the function np.mean() to get the desired function
# mean_stream.
def mean_stream(list_of_streams):
    return stream_func(inputs=list_of_streams,
                       f_type='element',
                       f=np.mean,
                       num_outputs=1)


#______________________________________________________
# PART 5B: Merge Stateful
# Two or more inputs, single output, stateful functions.
# A python function with two parameters: (1) a list
# and (2) a state, and that returns two values: (1) a
# single element of a stream and (2) a new state, is
# wrapped to obtain a function that has as input a
# list of streams and outputs a single stream.
#

#          EXAMPLE 1

# SPECIFICATION:
# Write a function, max_stream that has a single parameter,
# a list of input streams, and that outputs a single stream.
# The elements of all the input streams are nonnegative
# numbers.
# The elements of the output stream are 3-tuples:
# (0) max value seen so far in all the inputs,
# (1) index of the list in which max value appears, and
# (3) the time, i.e., the count, at which the max value appeared.
# For example, if the list of input streams is [x, y] where
# x = [10, 9, 3, 0, 7, 8, 10] and y = [8, 8, 4, 9, 12, 2, 3]
# then the output stream would be [(10, 0, 0), (12, 1, 4)] because
# x[0]=10 and y[4]=12 are the max values seen, and x is the
# zeroth element of the input list, while y is the first element
# of the input list.

# First step:
# The state of the computation is  a 2-tuple:
# (0) the previous max value,
# (1) the current time (count).

# Write a function, max_with_index,
# with two parameters: a list of numbers and a state.
# The function returns a 2-tuple: (msg, next_state).

# At each step, the current time is incremented by 1.
# msg is _no_value to indicate no message or is the
# 3-tuple (current max, current max index, current time).

def max_with_index(list_of_numbers, state):
    previous_max, current_time = state
    current_max = max(list_of_numbers)
    current_time += 1
    if previous_max >= current_max:
        msg = _no_value
        state = (previous_max, current_time)
    else:
        current_max_index = list_of_numbers.index(current_max)
        msg = (current_max, current_max_index, current_time)
        state = (current_max, current_time)
    return (msg, state)

# Second step:
# Wrap the function, max_with_index, to get the desired function
# max_stream.
def max_stream(list_of_streams):
    return stream_func(inputs=list_of_streams,
                       f_type='element',
                       f=max_with_index,
                       num_outputs=1,
                       state=(-1, -1) # Initial (max, time)
                       )




#######################################################
#            PART 6: MANY TO MANY
# TWO OR MORE INPUT STREAMS, TWO OR MORE OUTPUT STREAMS.
#
#######################################################

#______________________________________________________
# PART 6A: Many to Many Stateless

# A python function with a single parameter, a list
# of stream elements and that returns a single value: a
# list of stream elements is wrapped to obtain a function
# that inputs a list of streams and that ouputs a list
# of streams
#

#          EXAMPLE 1

# SPECIFICATION:
# Write a function, inrange_and_outlier_streams, with the
# following parameters: a list of two streams and constants
# A, B, DELTA. We call the two input streams x_stream and
# y_stream. The elements of the input streams are numbers.
# The function returns a list of two streams that we call
# inrange_stream and outlier_stream. A pair of inputs
# (x, y) from the input streams x_stream, y_stream is placed
# in inrange_stream if abs(A*x+B - y) <= DELTA, and
# in outlier_stream otherwise.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function, inrange_and_outlier_values, with a
# single parameter, a list of two values, where the values
# are elements of streams. The function uses constants
# A, B, DELTA which are defined outside the function.
# The function returns a list of two values which will
# be output on inrange_stream and outlier_stream. The
# function returns _no_value to indicate that no value
# is output.

# Second step:
# Wrap the function, inrange_and_outlier_values, to get
# the function, inrange_and_outlier_streams.
    
def inrange_and_outlier_streams(
        x_and_y_streams, A, B, DELTA):

    def in_range_and_outlier_values(x_and_y):
        x, y = x_and_y
        if abs(A*x+B-y) > DELTA:
            return ([_no_value, x_and_y])
        else:
            return ([x_and_y, _no_value])

    return stream_func(
        inputs=x_and_y_streams,
        f_type='element',
        f=in_range_and_outlier_values,
        num_outputs=2)


#______________________________________________________
# PART 6A: Many to Many Stateful

# Start with a python function with two parameters, a list
# of stream elements and a state; the function returns a
# list of stream elements and a new state. We wrap this 
# function to obtain a function that takes a list of
# streams as input and that ouputs a list of streams.
#

#          EXAMPLE 1

# SPECIFICATION:
# Write a function similar to that of Section 5B
# (Merge, Stateful), example 1. Write max_and_min
# which takes a list of streams as input and outputs
# two streams. One of the output streams contains the
# max value seen so far, and the time at which the
# this max value was received and the other contains the
# same for the min value.
# The elements of the input streams are nonnegative
# numbers less than 10000.

# See Section 5B, example 1. A difference with the
# example in 5B is that the output streams contain
# the names of streams rather than their indexes.
# The wrapped function, max_and_min_with_names,
# must have access to the stream names. So the
# wrapped function is defined inside the stream
# function, max_and_min_stream.

def max_and_min_with_names(list_of_numbers, state):
    previous_max, previous_min, current_time = state
    current_max = max(list_of_numbers)
    current_min = min(list_of_numbers)
    current_time += 1

    if previous_max >= current_max:
        msg_max = _no_value
    else:
        max_index = list_of_numbers.index(current_max)
        max_stream_name = list_of_streams[max_index].name
        msg_max = (current_max, max_stream_name, current_time)
        previous_max = current_max

    if previous_min  <= current_min:
        msg_min = _no_value
    else:
        min_index = list_of_numbers.index(current_min)
        min_stream_name = list_of_streams[min_index].name
        msg_min = (current_min, min_stream_name, current_time)
        previous_min = current_min

    state = (previous_max, previous_min, current_time)
    msgs_max_and_min = [msg_max, msg_min]

    return (msgs_max_and_min, state)


# Second step:
# Wrap the function, max_with_index, to get the desired function
# max_stream.
def max_and_min_stream(list_of_streams):

    def max_and_min_with_names(list_of_numbers, state):
        previous_max, previous_min, current_time = state
        current_max = max(list_of_numbers)
        current_min = min(list_of_numbers)
        current_time += 1

        if previous_max >= current_max:
            msg_max = _no_value
        else:
            max_index = list_of_numbers.index(current_max)
            max_stream_name = list_of_streams[max_index].name
            msg_max = (current_max, max_stream_name, current_time)
            previous_max = current_max

        if previous_min  <= current_min:
            msg_min = _no_value
        else:
            min_index = list_of_numbers.index(current_min)
            min_stream_name = list_of_streams[min_index].name
            msg_min = (current_min, min_stream_name, current_time)
            previous_min = current_min

        state = (previous_max, previous_min, current_time)
        msgs_max_and_min = [msg_max, msg_min]

        return (msgs_max_and_min, state)
    # Finished def max_and_min_with_names

    # Wrapper
    return stream_func(inputs=list_of_streams,
                       f_type='element',
                       f=max_and_min_with_names,
                       num_outputs=2,
                       state=(-1, 10000, -1) # Initial (max, min, time)
                       )


def main():
    
    # Illustration of timer: Part 3. Example 1
    # and print_stream: Part 2a. Example 2

    # Create a stream x and call it
    # 'natural numbers'
    x = Stream('natural numbers')
    # Create an agent that prints the stream
    print_stream(x)
    # call function timer to populate the stream
    timer(
        output_stream=x,
        num_outputs=5,
        time_period=0.1)

    ################################################
    #         PART 1a
    ################################################
    
    ################################################
    print
    print 'Part 1a. Example 1'
    # Illustration of square_stream
    # Create a stream y whose elements are the squares
    # of the elements of x.
    y = square_stream(x)
    # Give the stream a name.
    # A name helps in reading the output.
    y.set_name('Squares of x')
    print_stream(y)

    ################################################
    print
    print 'Part 1a. Example 2'
    # Illustration of double_stream. Part 1a. Example 2
    # Create a stream z whose elements are twice the
    # elements of x
    z = double_stream(x)
    # Give the stream a name and print it.
    z.set_name('Doubles of x')
    print_stream(z)

    ################################################
    print
    print 'Part 1a. Example 3'
    w1 = double_stream(square_stream(x))
    w2 = square_stream(double_stream(x))
    w1.set_name('Doubles of squares of x')
    w2.set_name('Squares of doubles of x')
    print_stream(w1)
    print_stream(w2)

    ################################################
    print
    print 'Part 1a. Example 4'
    v = discard_odds(x)
    v.set_name('Even numbers in x')
    print_stream(v)

    v1 = discard_odds_1(x)
    v1.set_name('Even numbers or None in x')
    print_stream(v1)

    ################################################
    print
    print 'Part 1a. Example 5'
    u = evens_and_halves(x)
    u.set_name('Evens and halves of evens in x')
    print_stream(u)

    u3 = evens_and_halves_3(x)
    u3.set_name('Tuples of evens and halves of evens in x')
    print_stream(u3)

    ################################################
    print
    print 'Part 1a. Example 6'
    s = multiply_elements_in_stream(stream=x, multiplier=3)
    s.set_name('Three times x')
    print_stream(s)

    ################################################
    print
    print 'Part 1a. Example 7'
    r = boolean_of_values_greater_than_threshold(
        stream=x, threshold=2)
    r.set_name('Indicator of values above 2 in x')
    print_stream(r)


    ################################################
    #   PART 1B
    ################################################

    ################################################
    print
    print 'Part 1b. Example 1'
    q = cumulative_stream(x)
    q.set_name('Cumulative sum of x')
    print_stream(q)

    ################################################
    print
    print 'Part 1b. Example 2'
    o = average_stream(x)
    o.set_name('Average of x')
    print_stream(o)


    ################################################
    #   PART 2: SINKS
    ################################################

    ################################################
    print
    print 'Part 2. Example 1'
    print0(x)

    ################################################
    print
    print 'Part 2. Example 2'
    print_stream(x)

    stream_to_file(x, 'temp')

    
    ################################################
    #   PART 3: SOURCES
    ################################################

    ################################################
    print
    print 'Part 3. Example 2'
    c = Stream('Random numbers')
    rand(output_stream=c, num_outputs=5, time_period=0.05)
    print_stream(c)

    ################################################
    print
    print 'Part 3. Example 3'
    b = Stream('stream from file temp')
    print_stream(b)
    file_to_stream('temp', b)

    ################################################
    print
    print 'Part 3. Example 4'
    a = single_stream_of_random_numbers(x)
    a.set_name('Stream of random numbers triggered by x')
    print_stream(a)
    
    
    ################################################
    #   PART 4A: SPLIT. STATELESS
    ################################################

    ################################################
    print
    print 'Part 4. Example 1'
    sqr, dbl = square_and_double_stream(x)
    sqr.set_name('square of x')
    dbl.set_name('twice x')
    print_stream(sqr)
    print_stream(dbl)

    ################################################
    print
    print 'Part 4. Example 2'
    exp, mul, div = \
      exp_mult_div_stream(
          stream=x, exponent=3, multiplier=10, divisor=0.25)
    exp.set_name('raise to 3rd power of x')
    mul.set_name('multiply 10 times x')
    div.set_name('divide by 0.25 of x')
    print_stream(exp)
    print_stream(mul)
    print_stream(div)

    
    ################################################
    print
    print 'Part 4. Example 3'
    evens, odds = even_odd_stream(x)
    evens.set_name('even values of x')
    odds.set_name('odd values of x')
    print_stream(evens)
    print_stream(odds)

        
    ################################################
    #   PART 4B: SPLIT. STATEFUL
    ################################################
    
    ################################################
    print
    print 'Part 4B. Example 1'
    input_temp_humid_stream = Stream('input temperature and humidity')
    print_stream(input_temp_humid_stream)
    input_temp_humid_stream.extend([
        ('temperature', 2015101501, 60),
        ('humidity', 2015101501, 30),
        ('temperature', 2015101502, 61),
        ('temperature', 2015101503, 62),
        ('humidity', 2015101503, 31),
        ('temperature', 2015101504, 63),
        ('temperature', 2015101505, 65),
        ('humidity', 2015101505, 32)
        ])
    
    temperature_stream, humidity_stream = \
      temperature_and_humidity_streams(input_temp_humid_stream, DELTA=1)
    temperature_stream.set_name('changing temperatures')
    humidity_stream.set_name('changing humidities')
    print_stream(temperature_stream)
    print_stream(humidity_stream)

    
    ################################################
    #   PART 5A: MERGE. STATELESS
    ################################################

    ################################################
    print
    print 'Part 5A. Example 1'
    aaa = Stream('aaa')
    bbb = Stream('bbb')
    ccc = Stream('ccc')
    print_stream(aaa)
    print_stream(bbb)
    print_stream(ccc)
    ddd = mean_stream([aaa, bbb, ccc])
    ddd.set_name('mean of aaa, bbb, ccc')
    print_stream(ddd)
    aaa.extend([30, 25, 50, 6, 10])
    bbb.extend([10, 15, 70, 8, 6])
    ccc.extend([20, 21, 30, 4])


   
    ################################################
    #   PART 5B: MERGE. STATEFUL
    ################################################

    ################################################
    print
    print 'Part 5B. Example 1'
    eee = max_stream([aaa, bbb, ccc])
    eee.set_name('max of aaa, bb, ccc')
    print_stream(eee)


   
    ################################################
    #   PART 6: MANY TO MANY. STATELESS
    ################################################

    ################################################
    print
    print 'Part 6A. Example 1'
    xx = Stream('x_stream')
    yy = Stream('y_stream')
    
    inrange_stream, outlier_stream = \
      inrange_and_outlier_streams(
        x_and_y_streams=[xx,yy],
        A=2, B=1, DELTA=2)

    inrange_stream.set_name('inrange')
    outlier_stream.set_name('outlier')
    print_stream(inrange_stream)
    print_stream(outlier_stream)

    xx.extend([3, 5, 8, 4, 6, 2])
    yy.extend([7, 14, 2, 10, 12, 9])


    ################################################
    print
    print 'Part 6B. Example 1'
    max_stream_2, min_stream_2 = max_and_min_stream([aaa, bbb, ccc])

    max_stream_2.set_name('max from max_and_min of aaa, bbb, ccc')
    min_stream_2.set_name('min from max_and_min of aaa, bbb, ccc')

    print_stream(max_stream_2)
    print_stream(min_stream_2)
    
if __name__ == '__main__':
    main()

