"""This module contains examples of the 'window' wrapper.
A window wrapper wraps a function that has a parameter which
is a list or a list of lists and that returns a value or a
list of values. The wrapped function operates on a sliding
window of a stream or a list of sliding windows of a list of
streams, and returns a stream or a list of streams.

A sliding window is defined by a window size and a step size.
An operation on a sliding window carries out its first operation
only when the size of the stream is at least the window size.
A window is a list of the specified size. An operation is carried
out on the window; then the window is moved forward in the stream
by the step size.

For example, if the operation on the window is sum, and the window
size is 3 and the step size is 2, and the stream is [5, 7] at
a point in time t0, then no window operation is carried at t0.
If at a later time, t1, the stream is [5, 7, 8] then the sum operation
is carried out on this window of size 3 to return 20 at t1. Then the
window operation waits until the window steps forward by 2. If at
a later time, t2, the stream is [5, 7, 8, 2], no operation is
carried out at t2. At a later time t3, if the stream is [5, 7, 8, 2, 5]
then an operation is carried out on the window [8, 2, 5] to give 15.

A window operation on multiple input streams waits until sliding windows
are available on all the input streams. The window sizes and step sizes
for all windows are identical.

The examples below deal with stateless and stateful cases of single and
multiple input streams and single and multiple output streams. We don't
use windows for sources or for sinks because simple elements are adequate
for this purpose. Likewise, we don't use windows for asynchronous merges.

"""

from Stream import Stream, _no_value, _multivalue
from Operators import stream_func, stream_agent
from examples_element_wrapper import print_stream
import numpy as np
import random

#######################################################
#######################################################
#            PART 1
#   SINGLE INPUT STREAM, SINGLE OUTPUT STREAM.
#######################################################
#######################################################

#----------
#STATELESS
#----------

# Window size and step size and N, the length of the
# input stream for the examples are specified next:
window_size = 100
step_size = 50
N = 500

#_____________________________________________________
# EXAMPLE 1. MEAN OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function that has a single  input stream and
# that returns a stream whose elements are the means of
# sliding windows of its input stream. The size of the
# window and the step_size (i.e., how far the window
# moves on each step) are parameters of the function.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that has a parameter that
# is a list or array and that returns the mean of that
# list or array. np.mean is such a function.

# Second step:
# Wrap the function using the wrapper, stream_func,
# in the same way as was done for the element_wrapper.
# This function returns a stream; we call that
# stream mean_of_x.

# The input stream for this example is x
x = Stream('x: stream of random numbers')

# The wrapper operates on the single input
# stream, x, to return a stream mean_of_x.
mean_of_x = stream_func(
    inputs=x, # A single stream
    f_type='window', # Identifies the 'window' wrapper
    f=np.mean, # The function that is wrapped
    num_outputs=1, # Returns a single stream
    window_size=window_size,
    step_size=step_size)

# Give the stream a name
mean_of_x.set_name('Mean of x')
# Create an agent to print the stream.
print_stream(mean_of_x)


#_____________________________________________________
#_____________________________________________________
# EXAMPLE 1A. SAME EXAMPLE USING AGENTS
#_____________________________________________________
#_____________________________________________________
#          MEAN OF SLIDING WINDOW
# USES STREAM_AGENT RATHER THAN STREAM_FUNC
#_____________________________________________________


mean_of_x_a = Stream('Mean of x for agent')
stream_agent(
    inputs=x,
    outputs=mean_of_x_a,
    f_type='window',
    f=np.mean,
    window_size=window_size,
    step_size=step_size)
print_stream(mean_of_x_a)

 
# Drive the example.
# Add values to stream x.
x.extend([random.random() for _ in range(N)])

#_____________________________________________________
# EXAMPLE 2. STANDARD DEVIATION OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function that has a single  input stream and
# that returns a stream whose elements are the standard
# deviations of sliding windows of its input stream.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that has a parameter that
# is a list or array and that returns the standard
# deviation of that list or array. np.std is such a
# function.

# Second step:
# Wrap the function using the wrapper, stream_func,
# in the same way as was done for the element_wrapper.
# This function returns a stream; we call that
# stream std_of_y.

# The input stream for this example is y
y = Stream('y: stream of random numbers')

# The wrapper operates on the single input
# stream, y, to return a stream std_of_y.
std_of_y = stream_func(
    inputs=y, # a single stream
    f_type='window', # identifies the 'window' wrapper
    f=np.std, # The wrapped function
    num_outputs=1, # Returns a single stream
    window_size=window_size,
    step_size=step_size)

# Set the name of the stream returned by the function.
std_of_y.set_name('Standard deviation of y')
# Create an agent that prints the stream.
print_stream(std_of_y)

# Drive the example.
# Add values to stream y.
y.extend([random.random() for _ in range(N)])


#_____________________________________________________
# EXAMPLE 3. SUM OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function that has a single  input stream and
# that returns a stream whose elements are the sums
# of sliding windows of its input stream.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that has a parameter that
# is a list or array and that returns the sum of that
# list or array. sum is such a function.

# Second step:
# Wrap the function using the wrapper, stream_func,
# in the same way as was done for the element_wrapper.
# This function returns a stream; we call that
# stream sum_of_z.

# The input stream for this example is z
z = Stream('z: stream of random numbers')

# The wrapper operates on the single input
# stream, z, to return a stream sum_of_z.
sum_of_z = stream_func(
    inputs=z, # A single stream
    f_type='window', # Identifies the 'window' wrapper
    f=sum, # The wrapped function
    num_outputs=1, # Returns a single stream
    window_size=window_size,
    step_size=step_size)

# Set the name of the stream returned by the function.
sum_of_z.set_name('Sum of z')
# Create an agent that prints the stream.
print_stream(sum_of_z)

# Drive the example.
# Add values to stream z.
z.extend([random.random() for i in range(N)])

#_____________________________________________________
# EXAMPLE 4. MAX - MIN OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function that has a single input stream and
# that returns a stream whose elements are the max - min
# of sliding windows of its input stream.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that has a parameter that
# is a list or array and that returns the max - min of that
# list or array.
def extent(lst):
    return max(lst) - min(lst)

# Second step:
# Wrap the function using the wrapper, stream_func,
# in the same way as was done for the element_wrapper.


# The input stream for this example is w
w = Stream('w: stream of random numbers')

# The wrapper operates on the single input
# stream, w, to return a stream extent_of_w.
extent_of_w = stream_func(
    inputs=w, # A single stream
    f_type='window', # Identifies 'window' wrapper
    f=extent, # The function that is wrapped
    num_outputs=1, # Returns a single stream
    window_size=window_size,
    step_size=step_size)

# Set the name of the stream returned by the function.
extent_of_w.set_name('Extent of w')
# Create an agent that prints the stream
print_stream(extent_of_w)

# Drive the example.
# Add values to stream w.
w.extend([random.random() for _ in range(N)])

#----------
#STATEFUL
#----------

#_____________________________________________________
# EXAMPLE 5. LINEAR COMBINATION OF WINDOW ELEMENTS
#_____________________________________________________

# SPECIFICATION:
# Write a function combine_window that has two parameters:
# (1) a single input stream and
# (2) weights: a list of nonnegative floats that sum to 1.0
#              where the length of the list is one more than
#              the length of the window
# The function returns a stream whose elements are the weights
# multipled by the window values.
# Example: window_size is 2. weights=[0.2, 0.3, 0.5]
# input_stream = [1, 4, 8, 10, 2,......]
# output_stream = [(1*0.2 + 4*0.3 + 8*0.5),
#                  (4*0.2, 8*0.3, 10*0.5),
#                  (8*0.2, 10*0.3, 2*0.5)

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function dot_product_window_with_weights
# with a single parameter, window_list, which is a
# list. The function has access to weights which is
# defined outside the function.
#

# Second step:
# Wrap the function using the wrapper, stream_func.
def combine_windows(input_stream, weights):
    
    def dot_product_window_with_weights(window_list):
        assert len(window_list) == len(weights)
        return np.dot(window_list, weights)
    
    return stream_func(
        inputs=input_stream, # A single stream
        f_type='window', # Identifies 'window' wrapper
        f=dot_product_window_with_weights,
        num_outputs=1, # Returns a single stream
        window_size=len(weights),
        step_size=1 # The window always moves by 1
        )
        
# The input stream for this example is ww
ww = Stream('ww')
# The output stream is uu
uu = combine_windows(input_stream=ww, weights=[0.2, 0.8])
uu.set_name('Combine_windows_ww')
print_stream(uu)
print_stream(ww)

# Drive the example.
# Add values to stream w.
ww.extend([10, 5, 25, 20, 40, 5])



#-----------------------------------------------------
#-----------------------------------------------------
#STATEFUL
#-----------------------------------------------------
#-----------------------------------------------------

#_____________________________________________________
# EXAMPLE 1. MEAN (INCREMENTAL) OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function that has a single input stream and
# that returns a stream whose elements are the means
# of sliding windows of its input stream. The step size
# is 1. The mean is computed incrementally by including
# the single new element entering the window as the
# window moves forward and deleteing the single element
# that drops out of the window.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that has two parameters: a list
# and a state where the state is a tuple:
# (sum_window, next_value_dropped).
# sum_window is the sum of the window.
# value_dropped is the zeroth element of the
# window.
def mean_inc(lst, state):
    sum_window, value_dropped = state
    # sum_window is the sum of the last window
    # value_dropped is the zeroth element of the
    # last window.
    # next_sum_window is the sum of the next window.
    # next_value_dropped is the zeroth element of the
    # next window.
    if sum_window is None:
        # This is the first window
        next_sum_window = sum(lst)
    else:
        # lst[-1] is the element entering the window as
        # it slides forward, and next_value_dropped is
        # the element leaving the window.
        next_sum_window = sum_window + lst[-1] - value_dropped
    mean = next_sum_window/float(len(lst))
    next_value_dropped = lst[0]
    state = (next_sum_window, next_value_dropped)
    return (mean, state)

# Second step:
# Wrap the function using the wrapper, stream_func,
# in the same way as was done for the element_wrapper.
def mean_of_window(stream):
    return stream_func(
        inputs=stream, # A single stream
        f_type='window', # Identifies the 'window' wrapper
        f=mean_inc, # The wrapped function
        num_outputs=1, # The wrapper returns a single stream
        state=(None, None), # Initial state
        window_size=100,
        step_size=1 # step_size is 1 for incremental computation.
        )


# The input stream for this example is v
v = Stream('v: stream of random numbers')

mean_of_v_computed_incrementally = mean_of_window(v)
mean_of_v_computed_incrementally.set_name(
    'mean of v computed incrementally')
print_stream(mean_of_v_computed_incrementally)

# Add values to stream v.
v.extend([random.random() for _ in range(110)])


#_____________________________________________________
#_____________________________________________________
#  SAME EXAMPLE, CREATING AGENT RATHER THAN A STREAM
# EXAMPLE 1A. MEAN (INCREMENTAL) OF SLIDING WINDOW
#_____________________________________________________
#_____________________________________________________

mean_using_agents = Stream('Mean using agents')
print_stream(mean_using_agents)
stream_agent(
    inputs=v, # A single stream
    outputs=mean_using_agents,
    f_type='window', # Identifies the 'window' wrapper
    f=mean_inc, # The wrapped function
    state=(None, None), # Initial state
    window_size=100,
    step_size=1 # step_size is 1 for incremental computation.
    )

#######################################################
#            PART 2: SPLIT
#      SINGLE INPUT STREAM, TWO OR MORE OUTPUT STREAMS.
#######################################################

#----------
#STATELESS
#----------

#_____________________________________________________
# EXAMPLE 1. MAX AND MIN OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function that has a single input stream and
# that returns a list of two streams whose elements are
# the max and the min of sliding windows of its input stream.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function that has a single parameter, a list,
# and that returns a tuple of two values: the max and the
# min of the list.
def max_and_min(lst): return (max(lst), min(lst))

# Second step:
# Wrap the function using the wrapper, stream_func,
# in the same way as was done for the element_wrapper.

# The input stream for this example is u
u = Stream('u: stream of random numbers')

# The wrapper returns a list of two streams:
# max_of_u, min_of_u
max_of_u, min_of_u = stream_func(
    inputs=u, # A single stream
    f_type='window', # Identifies the 'window' wrapper
    f=max_and_min, # The wrapped function
    num_outputs=2, # The wrapper returns a list of two output streams.
    window_size=window_size,
    step_size=step_size)

max_of_u.set_name('max of u')
min_of_u.set_name('min of u')
print_stream(max_of_u)
print_stream(min_of_u)

# Drive the example.
# Add values to stream u.
u.extend([random.random() for _ in range(N)])


#----------
#STATEFUL
#----------

#_____________________________________________________
# EXAMPLE 1. EXPONENTIAL SMOOTHED MEAN, STANDARD DEVIATION
#                 OF SLIDING WINDOW
#_____________________________________________________

# SPECIFICATION:
# Write a function
#      exp_smoothing_mean_and_std_of_stream
# with the following parameters:
#     stream, alpha, window_size, step_size
# where:
# stream is an input stream
# alpha is the exponential smoothing parameter
# window_size, step_size are the window and step sizes.
# The function returns a list of two streams whose elements
# are the smoothed mean and standard deviation of sliding
# windows of its input stream.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function,
#       exp_smoothing_mean_and_std_of_list,
# that has two parameters, a list and a state
# It returns a 2-tuple of messages and a new state.
# The first message in the 2-tuple is appended to
# the output stream of means, and the second message
# of the 2-tuple is appended to the output stream of
# standard deviations.
#
# Second step:
# Wrap the function using stream_func.
def exp_smoothing_mean_and_std_of_stream(
        stream, alpha, window_size, step_size):
    def exp_smoothing_mean_and_std_of_list(lst, state):
        alpha = 0.8
        a = np.array(lst)
        #m is mean. s is standard deviation.
        m, s = state
        m = (1-alpha)*m + alpha*a.mean()
        s = (1-alpha)*s + alpha*a.std()
        state = (m,s)
        tuple_of_messages = (m,s)
        return (tuple_of_messages, state)
    return stream_func(
        inputs=stream, # A single Stream
        f_type='window', # Identifies the 'window' wrapper
        f=exp_smoothing_mean_and_std_of_list, # The wrapped function
        num_outputs=2, # The wrapper returns a list of two output streams.
        state=(10.5, 0.29), # Initial estimates of mean, std
        window_size=window_size,
        step_size=step_size)

# The input stream for this example is t
t = Stream('t: stream of random numbers')
# The wrapper operates on the single input
# stream, t, to return a list of two streams:
# smoothed_mean_of_t, smoothed_std_of_t.
smoothed_mean_of_t, smoothed_std_of_t = \
  exp_smoothing_mean_and_std_of_stream(
      stream=t, alpha=0.5, window_size=50, step_size=50)
  
smoothed_mean_of_t.set_name('smoothed mean of t')
smoothed_std_of_t.set_name('smoothed std of t')
print_stream(smoothed_mean_of_t)
print_stream(smoothed_std_of_t)

# Drive the example.
# Add values to stream t. Exponential smoothing will
# result in the mean initially being around 10.0 and then
# eventually reducing to 0.0, and the standard deviation
# remaining unchanged at about 0.29. 
t.extend([10+random.random() for _ in range(500)])
t.extend([random.random() for _ in range(500)])


#######################################################
#            PART 3: SYNCHRONOUS MERGE
#      TWO OR MORE INPUT STREAMS, SINGLE OUTPUT STREAM.
#######################################################

#----------
#STATELESS
#----------

#_____________________________________________________
# EXAMPLE 1. DIFFERENCE OF MEANS OF TWO SLIDING WINDOWS
#_____________________________________________________


def diff_of_means_of_two_windows(list_of_two_windows):
    first_window, second_window = list_of_two_windows
    return np.mean(first_window) - np.mean(second_window)

# The two input streams for this example are r and s.
s = Stream('s: stream of random numbers')
r = Stream('r: stream of random numbers')

# diff_means is the stream of differences between the means
# of the moving windows of streams r and s.
diff_means = stream_func(
    inputs=[r, s], # A list of streams
    f_type='window', # Identifies the 'window' wrapper
    f=diff_of_means_of_two_windows, # The wrapped function
    num_outputs=1, # The wrapper returns a single output stream.
    window_size=50,
    step_size=50)

diff_means.set_name('Difference of means of windows')
print_stream(diff_means)

# Drive the example.
# Add values to streams r and s. 
for _ in range(5):
    s.extend([random.random() for _ in range(100)])
    r.extend([10+random.random() for _ in range(100)])


#----------
#STATEFUL
#----------

#_____________________________________________________
# EXAMPLE 1. DIFFERENCE OF AVERAGES OF TWO SLIDING WINDOWS
#_____________________________________________________

# SPECIFICATION:
# Write a function with a parameter that is a list of
# two input streams, window size and step size. The function
# returns an output stream where the elements of the output
# stream are the averages of the differences in means of
# the windows into the two input streams.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function
# avg_of_difference_of_two_windows
# that has two parameters, a list of two windows (recall that
# a window is a list) and a state which is the tuple:
# (cumulative_difference, count) where cumulative_difference
# is the sum of the differences over all instances as the
# two windows move forward in the streams, and count is the
# number of such instances. The initial value of state is
# set outside the function and is assumed to be (0.0, 0)

def avg_of_difference_of_two_windows(list_of_two_windows, state):
    cumulative_difference, count = state
    first_window, second_window = list_of_two_windows
    difference_in_means = np.mean(first_window) - np.mean(second_window)
    cumulative_difference += difference_in_means
    count += 1
    average = cumulative_difference/float(count)
    state = (cumulative_difference, count)
    message = average
    return (message, state)

p = Stream('p')
q = Stream('q')

# Second step:
# Wrap avg_of_difference_of_two_windows with the window
# wrapper (i.e., f_type='window') and set the initial
# state.
# The stream, avg_difference_of_means, is returned by
# the wrapping function for input streams p and q.
avg_difference_of_means = \
  stream_func(
    inputs=[p, q], # A list of streams
    f_type='window', # Identifies the 'window' wrapper
    f=avg_of_difference_of_two_windows,  # The wrapped function
    num_outputs=1, # The wrapper returns a single output stream.
    state = (0.0, 0), # Initial estimate of difference in means, and count
    window_size=50,
    step_size=50)

avg_difference_of_means.set_name(
    'average difference of means of windows')
print_stream(avg_difference_of_means)

# Drive the example.
# Add values to input streams p and q. 
for _ in range(5):
    # The average difference of means should be about 10.0
    p.extend([10+random.random() for _ in range(100)])
    q.extend([random.random() for _ in range(100)])



#######################################################
#            PART 4: MANY to MANY
#      TWO OR MORE INPUT STREAMS, TWO OR MORE OUTPUT STREAMS.
#######################################################

#----------
#STATELESS
#----------

#_____________________________________________________
# EXAMPLE 1. IN RANGE AND OUTLIER STREAMS
#_____________________________________________________

# SPECIFICATION:
# Write a function, inrange_and_outlier_streams,
# with the following parameters:
# a list of two input streams, window size, step size and
# threshold (a number).
# The function returns a list of two streams: (1) a stream
# of in-range values and (2) a stream of outlier values.
#
# The first input stream contains values that we
# call x-values and the second input stream contains
# values that we call y-values. The y values are in-range
# if they are near the corresponding x values, and
# are outliers otherwise. Specifically, if
# abs(y.mean() - x.mean()) <= threshold*x.std()
# then the y value is in range, where the mean and
# standard deviations are for windows into the streams.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# First step:
# Write a function, inrange_and_outlier_lists,
# that has a single parameters, a list of two windows
# (recall that a window is a list). It returns a list
# of two values which are messages to the in-range stream
# and the outlier stream, respectively.
# The returned list of two values are the y value and
# _no_value if the y value is in range. The two values
# are _no_value and the y_value if the y value is an
# outlier.
# The threshold parameter is specified outside the function.
#
# Second step:
# Wrap the function, inrange_and_outlier_lists, using
# the 'windows' wrapper to get the desired function:
# inrange_and_outlier_streams.

def inrange_and_outlier_streams(
        list_of_two_streams, window_size, step_size,
        threshold):

    # The function that is wrapped.
    def inrange_and_outlier_lists(list_of_two_windows):
        # Call the two windows, x and y, respectively.
        x, y = list_of_two_windows
        # Convert to numpy arrays to call numpy functions.
        x = np.array(x)
        y = np.array(y)
        if abs(y.mean() - x.mean()) <= threshold*x.std():
            # (x,y) is in range.
            # Return _no_value for the outlier stream.
            return ([y.mean(), _no_value])
        else:
            # (x,y) is an outlier
            # Return _no_value for the in-range stream.
            return ([_no_value, y.mean()])

    # The wrapper
    return stream_func(
        inputs=list_of_two_streams, # A list of streams
        f_type='window', # Indicates the 'window' wrapper
        f=inrange_and_outlier_lists, # Function that is wrapped.
        num_outputs=2, # Returns a list of two streams.
        window_size=window_size,
        step_size=step_size)


# Create and name the input streams of the function.
o_stream = Stream('input_0')
n_stream = Stream('input_1')

# The function returns a list of two streams.
inrange_stream, outlier_stream = \
  inrange_and_outlier_streams(
      list_of_two_streams=[o_stream, n_stream],
      window_size=10,
      step_size=10,
      threshold=1)

# Give names to the output streams and print them.
inrange_stream.set_name('inrange')
outlier_stream.set_name('outlier')
print_stream(inrange_stream)
print_stream(outlier_stream)

# Drive the example.
# Add values to input streams o_stream and n_stream.
# Most of the output values should be in range because they
# are uniform random numbers in the interval (0.0, 1.0).
o_stream.extend([random.random() for _ in range(100)])
n_stream.extend([random.random() for _ in range(100)])

# More output values will be outliers because the elements of
# o_stream are the sum of two uniform random numbers.
o_stream.extend(
    [random.random() + random.random() for _ in range(100)])
n_stream.extend([random.random() for _ in range(100)])


#----------
#STATEFUL
#----------

#_____________________________________________________
# EXAMPLE 1. IN RANGE AND OUTLIER STREAMS WITH
#          EXPONENTIAL SMOOTHING OF THE THRESHOLD.
#_____________________________________________________

# SPECIFICATION:
# The specification is similar to that of the stateless
# case except that the threshold is exponentially smoothed
# at each step. The state of the system is the threshold. 

def inrange_and_outlier_streams(
        list_of_two_streams, window_size, step_size,
        alpha, # The exponential smoothing parameter
        threshold):

    # The function that is wrapped.
    def inrange_and_outlier_windows(
            list_of_two_windows, # one window for each input stream
            state): # The state
        threshold, count = state
        # Call the two windows x and y
        x, y = list_of_two_windows
        x = np.array(x)
        y = np.array(y)
        num_standard_deviations = \
          abs(y.mean() - x.mean())/x.std()
        if num_standard_deviations <= threshold:
            # (x,y) is in range.
            inrange_value = (x.mean(), y.mean())
            outlier_value = _no_value
            # The output message
            message = [(count, inrange_value), outlier_value]
        else:
            # (x,y) is an outlier
            inrange_value = _no_value
            outlier_value = (x.mean(), y.mean())
            # The output message
            message = [inrange_value, (count, outlier_value)]

        # Exponentially smooth the current threshold to get
        # the new threshold.
        threshold = (num_standard_deviations * alpha
                     + threshold * (1 - alpha))
        count += 1
        # The next state
        state = (threshold, count)
        # Return the output message and the next state.
        return (message, state)

    # The wrapper
    return stream_func(
        inputs=list_of_two_streams,
        f_type='window', # Indicates the 'window' wrapper.
        f=inrange_and_outlier_windows, # The function that is wrapped.
        num_outputs=2, # Returns a list of two streams
        state=(0.0, 0), # Initial state, i.e., initial threshold, count
        window_size=window_size,
        step_size=step_size)

# Create and name the input streams of the function.
l_stream = Stream('l stream')
m_stream = Stream('m stream')

# The function returns a list of two streams.
inrange_exp_smooth_stream, outlier_exp_smooth_stream = \
  inrange_and_outlier_streams(
      list_of_two_streams=[l_stream, m_stream],
      window_size=20,
      step_size=20,
      alpha=0.9,
      threshold=1)

# Give names to the output streams and print them.
inrange_exp_smooth_stream.set_name('inrange exp smooth')
outlier_exp_smooth_stream.set_name('outlier exp smooth')
print_stream(inrange_exp_smooth_stream)
print_stream(outlier_exp_smooth_stream)

# Drive the example.
# Add values to input streams l_stream and m_stream.
# Most of the output values should be in range because they
# are uniform random numbers in the interval (0.0, 1.0).
for _ in range(100):
    x = random.random()
    l_stream.append(x)
    m_stream.append(x+0.01*random.random())
