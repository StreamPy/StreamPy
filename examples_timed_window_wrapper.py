
from Stream import Stream, _no_value, _multivalue, TimeAndValue
from Operators import stream_func, stream_agent
from examples_element_wrapper import print_stream
import numpy as np
import random


############################################################
############################################################
#  SECTION 1. SINGLE INPUT, SINGLE OUTPUT, STATELESS
############################################################
############################################################
print
print '**************************************************'
print 'SECTION 1'
print 'EXAMPLES OF SINGLE INPUT, SINGLE OUTPUT, STATELESS'
print '**************************************************'

#______________________________________________________
#
#   EXAMPLE 1: SINGLE INPUT, SINGLE OUTPUT, STATELESS
#______________________________________________________
print
print '--------------------------------------------------'
print 'SECTION 1. EXAMPLE 1 '
print '  SINGLE INPUT, SINGLE OUTPUT, STATELESS'
print '--------------------------------------------------'
#
# SPECIFICATION:
# Write a function that sums the values in a time-window
# in a single input stream. The elements of the input stream
# are TimeAndValue objects with a time field, and a value
# field. If x and y are elements in the stream and y follows
# x then y's timestamp is greater than x' timestamp.
# A window of length T time units includes exactly those
# elements in the stream with time stamps in the interval:
# [window_start_time : window_start_time + T].
# The window_start_time moves forward at each step by step_size
# time units; so the sequence of windows are
# [0 : T], [step_size : step_size + T],
# [2*step_size : 2*step_size + T], [3*step_size : 3*step_size + T]
# If window_size=4.0 and step_size=2.0 then the output stream
# will consist of the sum of the values with timestamps in the
# intervals [0:4], [2:6], [4:8], ...

# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP:
# Write a function on a timed list.
def sum_values_in_timed_list(timed_list):
    return sum(v.value for v in timed_list)

# a is the input stream for this example
a = Stream('a timed stream')
print_stream(a)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.
# z is the output stream for this example.
z = stream_func(
    inputs=a, # The input is a single stream
    f_type='timed', # Identifes 'timed' wrapper
    f=sum_values_in_timed_list, # Function that is wrapped.
    num_outputs=1, # Single output stream
    window_size=4.0,
    step_size=2.0)

z.set_name('sum of a')
print_stream(z)

# Drive the input streams.
t=0.0
for _ in range(20):
    t += random.random()
    v = random.randint(0,9)
    a.append(TimeAndValue(t, v))


############################################################
############################################################
# SECTION 2. SINGLE INPUT, SINGLE OUTPUT, STATEFUL
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 2'
print 'EXAMPLES OF SINGLE INPUT, SINGLE OUTPUT, STATEFUL'
print '**************************************************'

#_____________________________________________________________
#              EXAMPLE 1
#_____________________________________________________________


# SPECIFICATION:
# Write a function, exponential_smoothed_timed_windows,
# that computes func(window) for each
# timed window, where func is a parameter. The agent
# returns the exponentially smoothed value of func.
# The smoothing factor, alpha, is a parameter.


# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP:
# This computation has state to which smoothing is applied
# Write a function, exponential_smoothed_list, with
# parameters: a timed list and state. This function reads
# the parameter alpha of the stream function; so encapsulate
# exponential_smoothed_list within
# exponential_smoothed_timed_windows

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.

def exponential_smoothed_timed_windows(
        input_stream, func, alpha,
        window_size, step_size,
        initial_state):
    """
    Parameters

    ----------
    input_stream: Stream
           A previously defined stream
           This is the only input stream of the agent.
    func: function
          func operates on a list of TimeAndValue objects
          and returns an object that can be smoothed
          exponentially.
    alpha: number
          The exponential smoothing parameter.
    window_size, step_size, initial_state:
          Already defined.

    """
    
    def exponential_smoothed_list(timed_list, state):
        next_state = ((1 - alpha)*func(timed_list) +
                      alpha*state)
        message = next_state
        return (message, next_state)

    return stream_func(
        inputs=input_stream, # single input timed stream
        f_type='timed', # identifies 'timed' wrapper
        f=exponential_smoothed_list, # function that is wrapped
        num_outputs=1, # single output stream
        state=initial_state,
        window_size=window_size,
        step_size=step_size)

print
print '--------------------------------------------------'
print 'SECTION 2. EXAMPLE 1 '
print ' SINGLE INPUT, SINGLE OUTPUT, STATEFUL'
print '--------------------------------------------------'

# b is the input stream for this example
b = Stream('b: timed stream')
print_stream(b)

# y is the output stream for this example.
y = exponential_smoothed_timed_windows(
    input_stream=b,
    func=sum_values_in_timed_list,
    alpha=0.5,
    window_size=4,
    step_size=2,
    initial_state=0)

y.set_name('y')
print_stream(y)

# Drive the input
t=0.0
for _ in range(12):
    t += random.random()
    v = random.randint(0,9)
    b.append(TimeAndValue(t, v))


############################################################
############################################################
# SECTION 3.  MULTIPLE INPUTS, SINGLE OUTPUT, STATELESS
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 3'
print 'EXAMPLES OF MULTIPLE INPUTS, SINGLE OUTPUT, STATELESS'
print '**************************************************'


#______________________________________________________
#
# EXAMPLE 1: TWO OR MORE INPUT STREAMS, ONE OUTPUT STREAM
#   STATELESS
#______________________________________________________

# SPECIFICATION:
# Write a function that has a single parameter - a list of
# timed streams - and that returns the sum of the values of
# timed windows.
# For example, if the list consists of two timed streams, c
# and d, and:
# c = [(0.1, 100), (0.9, 200), (1.2, 500), (3.1. 800), (6.6, 300)]
# d = [(0.7, 5), (2.3, 25), (3.9, 12), (5.1, 18), (5.2, 12)]
# where for succinctness each pair is (time, value), then
# with a window size and step size of 1.0 the windows are:
# for c: [(0.1, 100), (0.9, 200)], [(1.2, 500)], [], [(3.1. 800)],
#        [], []..
# for d: [(0.7, 5)], [], [(2.3, 25)], [(3.9, 12)], [], ...
# Note that we don't yet have the complete windows for the
# interval [5.0, 6.0] for d because we may get later values
# with timestamps less than 6 on stream d.
# The sums for the windows are:
# (100+200+5), (500), (25), (800+12), (),


# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP:
# Write a function with a single parameter: a list of timed lists

def sum_values_in_all_timed_lists(list_of_timed_lists):
    return (sum(sum (v.value for v in timed_list)
                for timed_list in list_of_timed_lists))

print
print '--------------------------------------------------'
print 'SECTION 3. EXAMPLE 1 '
print ' MULTIPLE INPUTS, SINGLE OUTPUT, STATELESS'
print '--------------------------------------------------'

# Create input streams, c and d, for this example.
c = Stream('Input: c')
d = Stream('Input: d')
print_stream(c)
print_stream(d)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.

# x is the output stream for this example
x = stream_func(
    inputs=[c,d],  # list of two input timed streams
    f_type='timed', # identifies the 'timed' wrapper
    f=sum_values_in_all_timed_lists, #function that is wrapped
    num_outputs=1, # Single output stream
    window_size=2.0,
    step_size=2.0)

x.set_name('Output: x')
print_stream(x)

# Drive the input streams
t_c=0.0
t_d=0.0
for _ in range(12):
    t_c += random.random()
    t_d += random.random()
    v_c = random.randint(0,9)
    v_d = 100+random.randint(0,9)
    c.append(TimeAndValue(t_c, v_c))
    d.append(TimeAndValue(t_d, v_d))

    
#______________________________________________________
#
# EXAMPLE 2: TWO OR MORE INPUT STREAMS, ONE OUTPUT STREAM
#   STATELESS
#______________________________________________________

# SPECIFICATION:
# Write a function that has a two input streams and a
# single output stream. An element on the output stream is
# the difference in lengths of the two windows (one window
# per input stream).

# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP
# Write a function on a list of two lists.
def diff_of_counts_in_lists(list_of_two_lists):
    return len(list_of_two_lists[0]) - len(list_of_two_lists[1])


print
print '--------------------------------------------------'
print 'SECTION 3. EXAMPLE 2 '
print ' MULTIPLE INPUTS, SINGLE OUTPUT, STATELESS'
print '--------------------------------------------------'

# Create input streams, cc and dd, for this example.
cc = Stream('cc')
dd = Stream('dd')
print_stream(cc)
print_stream(dd)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.

# xx is the output stream for this example
xx = stream_func(
    inputs = [cc, dd], # Inputs is a list of two streams
    f_type = 'timed', # Identifies wrapper as the 'timed' wrapper
    f = diff_of_counts_in_lists, # Function that is wrapped
    num_outputs=1, # Single output stream.
    window_size=2.0,
    step_size=2.0)

xx.set_name('xx')
print_stream(xx)


# Drive the input streams
t_cc=0.0
t_dd=0.0
for _ in range(10):
    t_cc += random.random()
    t_dd += random.random()
    v_cc = random.randint(0,9)
    v_dd = random.randint(0,9)
    cc.append(TimeAndValue(t_cc, v_cc))
    dd.append(TimeAndValue(t_dd, v_dd))


############################################################
############################################################
#  SECTION 4. MULTIPLE INPUTS, SINGLE OUTPUT, STATEFUL
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 4'
print 'EXAMPLES OF MULTIPLE INPUTS, SINGLE OUTPUT, STATEFUL'
print '**************************************************'
#______________________________________________________
#
#  EXAMPLE 1. TWO OR MORE INPUT STREAMS, ONE OUTPUT STREAM
#           STATEFUL
#______________________________________________________
#
# SPECIFICATION:
# Write a function with a list of input streams that
# returns a stream in which element is a 2-tuple
# (max_so_far, max_of_current_window) where
# max_of_current_window is the max over all input
# streams of the sums of the values in each timed
# window, and
# max_so_far is the maximum value of max_of_current_window
# over all the windows seen thus far.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP:
# Write a function, max_sums_timed_windows, with two
# parameters: a list of timed lists, and a state.
# The state is the maximum value seen thus far.
# The function returns a message which is the 2-tuple
# (max_so_far, max_of_current_window), the maximum
# seen so far, and the current maximum, i.e., the
# maximum over all current windows of the sum of the
# window.

def max_sums_timed_windows(list_of_timed_lists, state):
    # The state is the max seen so far.
    max_so_far = state
    max_of_current_window = \
      max(sum(v.value for v in timed_list)
          for timed_list in list_of_timed_lists)
    # Update the max seen so far.
    max_so_far = max(max_so_far, max_of_current_window)
    message = (max_so_far, max_of_current_window)
    next_state = max_so_far
    return (message, next_state)

print
print '--------------------------------------------------'
print 'SECTION 4. EXAMPLE 1 '
print ' MULTIPLE INPUTS, SINGLE OUTPUT, STATEFUL'
print '--------------------------------------------------'

# Create input streams, ee and ff, for this example.
ee = Stream('ee')
ff = Stream('ff')
print_stream(ee)
print_stream(ff)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.

# w is the output stream of the wrapped function.
w = stream_func(
    inputs=[ee, ff], # list of two input timed streams
    f_type='timed', # Identifies 'timed' wrapper
    f=max_sums_timed_windows, # function being wrapped
    num_outputs=1, # Single output stream
    state = 0.0, # Initial state
    window_size=1.0,
    step_size=1.0)
w.set_name('w')
print_stream(w)

# Drive the input streams
t_ee=0.0
t_ff=0.0
for _ in range(8):
    t_ee += random.random()
    t_ff += random.random()
    v_ee = random.randint(0,9)
    v_ff = random.randint(0,9)
    ee.append(TimeAndValue(t_ee, v_ee))
    ff.append(TimeAndValue(t_ff, v_ff))


############################################################
############################################################
#  SECTION 5. SINGLE INPUT, MULTIPLE OUTPUT, STATELESS
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 5'
print 'EXAMPLES OF SINGLE INPUT, MULTIPLE OUTPUTS, STATELESS'
print '**************************************************'

#_____________________________________________________________
# EXAMPLE 1: SINGLE INPUT, TWO OR MORE OUTPUTS, STATELESS
#_____________________________________________________________

# SPECIFICATION:
# Write a function that has a single input stream and
# that returns two output streams containing the max
# the min values of windows of the input stream.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP:
# Write a function, max_sums_timed_windows, with two
# parameters: a list of timed lists

def max_and_min_of_values_in_timed_list(timed_list):
    if timed_list:
        return (max(v.value for v in timed_list),
                min(v.value for v in timed_list)
                )
    else:
        # timed_list is empty
        return (None, None)

print
print '--------------------------------------------------'
print 'SECTION 5. EXAMPLE 1 '
print ' SINGLE INPUT, MULTIPLE OUTPUT, STATELESS'
print '--------------------------------------------------'


# Create input stream, g, for this example.
g = Stream('g')
print_stream(g)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.

# u, v are the two output streams of the wrapped function.
u, v= stream_func(
    inputs=g, # Single input stream
    f_type='timed', # Identifies wrapper as 'timed' wrapper.
    f=max_and_min_of_values_in_timed_list, # function that is wrapped
    num_outputs=2, # Two output streams
    window_size=2.0,
    step_size=2.0)

u.set_name('u')
v.set_name('v')
print_stream(u)
print_stream(v)

# Drive the input stream.
t_g=0.0
for _ in range(10):
    t_g += random.random()
    v_g = random.randint(0,9)
    g.append(TimeAndValue(t_g, v_g))



############################################################
############################################################
#  SECTION 6. SINGLE INPUT, MULTIPLE OUTPUT, STATEFUL
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 6'
print 'EXAMPLES OF SINGLE INPUT, MULTIPLE OUTPUTS, STATEFUL'
print '**************************************************'

#_____________________________________________________________
# SECTION 6 EXAMPLE 1: SINGLE INPUT, TWO OR MORE OUTPUTS, STATEFUL
#_____________________________________________________________

# SPECIFICATION:
# Write a function that has a single input stream and
# that returns two output streams. The elements of the
# output stream are the average of the maximum values
# of the timed windows, where the average is taken
# over all the windows seen so far, and similarly for
# the minimum.

# HOW TO DEVELOP THE STREAMING PROGRAM.

# FIRST STEP:
# Write a function, avg_of_max_and_min_in_timed_list, with two
# parameters: a timed list and a state. The function returns
# a message and a (new) state. The message is a 2-tuple
# (avg_of_max, avg_of_min), where each element of the tuple
# becomes a message in a different output stream. The state
# is (num_windows, sum_of_max, sum_of_min) where
# num_windows is the number of time steps so far for which timed_list
# is non-empty.
# sum_of_max is the sum over all time steps of the max for each step.
# sum_of_min is the sum over all time steps of the min for each step.

def avg_of_max_and_min_in_timed_list(timed_list, state):
    num_windows, sum_of_max, sum_of_min = state
    if timed_list:
        # timed_list is nonempty
        next_max = max(v.value for v in timed_list)
        next_min = min(v.value for v in timed_list)
        num_windows += 1
        sum_of_max += next_max
        sum_of_min += next_min
        avg_of_max = sum_of_max/float(num_windows)
        avg_of_min = sum_of_min/float(num_windows)
        state = (num_windows, sum_of_max, sum_of_min)
        message = (avg_of_max, avg_of_min)
        return (message, state)
    else:
        # timed_list is empty
        # So, don't change the state.
        # In particular, don't increment num_windows
        avg_of_max = sum_of_max/float(num_windows)
        avg_of_min = sum_of_min/float(num_windows)
        message = (avg_of_max, avg_of_min)
        return (message, state)

print
print '--------------------------------------------------'
print 'SECTION 6. EXAMPLE 1 '
print ' SINGLE INPUT, MULTIPLE OUTPUTS, STATEFUL'
print '--------------------------------------------------'

# Create input stream, h, for this example.
h = Stream('h: Input stream')
print_stream(h)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.
# s_stream, t_stream are the two output streams of the wrapped function.
s_stream, t_stream = stream_func(
    inputs = h, # Input is a single stream.
    f_type = 'timed',
    f = avg_of_max_and_min_in_timed_list, # Function that is wrapped.
    num_outputs=2, # Two output streams
    state = (0, 0.0, 0.0), # Initial num windows, sum max, sum min
    window_size=2.0,
    step_size=2.0)

s_stream.set_name('avg max')
t_stream.set_name('avg min')
print_stream(s_stream)
print_stream(t_stream)

# Drive the input stream.
t_h=0.0
for _ in range(20):
    t_h += random.random()
    v_h = random.randint(0,9)
    h.append(TimeAndValue(t_h, v_h))


############################################################
############################################################
#  SECTION 7. MULTIPLE INPUTS, MULTIPLE OUTPUT, STATELESS
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 7'
print 'EXAMPLES OF MULTIPLE INPUTS, MULTIPLE OUTPUTS, STATELESS'
print '**************************************************'

#_____________________________________________________________
# SECTION 7 EXAMPLE 1: MULTIPLE INPUTS, MULTIPLE OUTPUTS, STATELESS
#_____________________________________________________________

# SPECIFICATION:
# Write a function that has a single parameter, a list of timed
# streams. The function returns a list of two (untimed) streams.
# The k-th element of the first output stream is the maximum
# value across all input streams of the k-th timed window, and
# the corresponding element for the second output stream is the
# minimum value. If the k-th timed windows for all the input
# streams are empty, the k-th element of the output streams are
# both None.


# FIRST STEP:
# Write a function that has a single parameter: a list of timed lists.
# The function returns a 2-tuple: the max and the min of the values
# across all the timed lists if at least one timed list is nonempty,
# and None otherwise.


def max_and_min_values_in_all_timed_lists(list_of_timed_lists):
    if any(list_of_timed_lists):
        return (max(max(v.value for v in timed_list)
                    for timed_list in list_of_timed_lists if timed_list),
                min(min(v.value for v in timed_list)
                    for timed_list in list_of_timed_lists if timed_list)
                )
    else:
        return (None, None)


print
print '--------------------------------------------------'
print 'SECTION 7. EXAMPLE 1 '
print ' MULTIPLE INPUTS, MULTIPLE OUTPUTS, STATELESS'
print '--------------------------------------------------'

# Create inputs stream, i_stream and j_stream, for this example.
i_stream = Stream('i_stream: Input stream')
j_stream = Stream('j_stream: Input stream')

# Print the streams so that you can visually check the results.
print_stream(i_stream)
print_stream(j_stream)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.
# q_stream, r_stream are the two output streams of the wrapped function.
q_stream, r_stream = stream_func(
    inputs = [i_stream, j_stream], # list of input timed_streams
    f_type = 'timed', # Identifies the 'timed' wrapper.
    f = max_and_min_values_in_all_timed_lists,
    num_outputs=2, # two output streams
    window_size=3.0,
    step_size=3.0)

q_stream.set_name('max of i_stream, j_stream timed windows')
r_stream.set_name('min of i_stream, j_stream timed windows')
print_stream(q_stream)
print_stream(r_stream)

# Drive the two input streams.
t_i=0.0
t_j=0.0
for _ in range(20):
    t_i += random.random()
    t_j += random.random()
    v_i = random.randint(0,9)
    v_j = random.randint(0,9)
    i_stream.append(TimeAndValue(t_i, v_i))
    j_stream.append(TimeAndValue(t_j, v_j))



############################################################
############################################################
#  SECTION 8. MULTIPLE INPUTS, MULTIPLE OUTPUT, STATEFUL
############################################################
############################################################

print
print '**************************************************'
print 'SECTION 8'
print 'EXAMPLES OF MULTIPLE INPUTS, MULTIPLE OUTPUTS, STATEFUL'
print '**************************************************'

#_____________________________________________________________
# SECTION 8 EXAMPLE 1: MULTIPLE INPUTS, MULTIPLE OUTPUTS, STATEFUL
#_____________________________________________________________

# SPECIFICATION:
# Section 8, example 1 is to Section 7, example 1, what
# Section 6, example 1 is to Section 5, example 1. The
# outputs in this example are the AVERAGES of the max and min
# over timed windows of all input streams (whereas in the
# previous example, the outputs were the max and min values
# without averaging).



# FIRST STEP:
# Write a function that has two parameters: a list of timed lists and
# a state.
# The function returns a tuple consisting of
# (1) a 2-tuple: the max and the min of the values of the timed lists
# (2) the next state.

def avg_of_max_and_min_values_in_all_timed_lists(list_of_timed_lists, state):
    num_windows, sum_of_max, sum_of_min = state
    if all(list_of_timed_lists):
        next_max = max(max(v.value for v in timed_list)
                       for timed_list in list_of_timed_lists)
        next_min = min(min(v.value for v in timed_list)
                       for timed_list in list_of_timed_lists)
        num_windows += 1
        sum_of_max += next_max
        sum_of_min += next_min
        avg_of_max = sum_of_max/float(num_windows)
        avg_of_min = sum_of_min/float(num_windows)
        state = (num_windows, sum_of_max, sum_of_min)
        return ([avg_of_max, avg_of_min], state)
    else:
        avg_of_max = sum_of_max/float(num_windows)
        avg_of_min = sum_of_min/float(num_windows)
        return ([avg_of_max, avg_of_min], state)

print
print '--------------------------------------------------'
print 'SECTION 8. EXAMPLE 1 '
print ' MULTIPLE INPUTS, MULTIPLE OUTPUTS, STATEFUL'
print '--------------------------------------------------'

# Create inputs stream, i_stream and j_stream, for this example.
k_stream = Stream('k_stream: Input stream')
l_stream = Stream('l_stream: Input stream')

# Print the streams so that you can visually check the results.
print_stream(k_stream)
print_stream(l_stream)

# SECOND STEP.
# Wrap the function with the 'timed' wrapper.
# o_stream, o_stream are the two output streams of the wrapped function.
o_stream, p_stream = stream_func(
    inputs = [k_stream, l_stream], # list of input timed_streams
    f_type = 'timed', # Identifies the 'timed' wrapper
    f = avg_of_max_and_min_values_in_all_timed_lists,
    num_outputs=2, # two output streams
    state= (0, 0.0, 0.0), # Initial num windows, sum_max, sum_min
    window_size=3.0,
    step_size=3.0)

o_stream.set_name('avg of max of k_stream, l_stream timed windows')
p_stream.set_name('avg of min of k_stream, l_stream timed windows')
print_stream(o_stream)
print_stream(p_stream)

# Drive the two input streams.
t_k=0.0
t_l=0.0
for _ in range(30):
    t_k += random.random()
    t_l += random.random()
    v_k = random.randint(0,9)
    v_l = random.randint(0,9)
    k_stream.append(TimeAndValue(t_k, v_k))
    l_stream.append(TimeAndValue(t_l, v_l))
