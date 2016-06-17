if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from scipy.signal import butter, lfilter
import sys
import numpy as np
import matplotlib.pyplot as plt
import math
from functools import partial
from Stream import Stream, _no_value, _multivalue
from Operators import stream_func
from Agent import Agent

def butter_bandpass(lowcut, highcut, fs, order=5):
    """
    Parameters
    -----------
    low_cut, high_cut: low and high cutoff for the bandpass
            filter in Hertz.
    fs: the sampling rate in Hertz (number of samples/second)
    order: the order of the filter. Higher order gives sharper
        filters.

    """
    
    nyq = 0.5 * fs # The Nyquist frequency
    low = lowcut / nyq # Unit-less value for the cutoff.
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def filter(b, a, input_stream):
    # b, a are lists of equal length.
    # b, a are obtained by calling scipy.butter_bandpass
    # The function filter returns the filtered stream.
    # The output is defined as follows:
    # For input sequence x, the output sequence y is:
    #  y[m] =
    # sum over j in [0,..,N]: x[m-j].b[j] -
    # sum over i in [1,..., N]: y[m-j].a[j]
    # where len(a) == len(b) and
    # N is len(b)-1.
    # Note that the second sum is subtracted from the first
    # sum
    window_size = len(b)
    # window_size is N+1
    # Convert the arrays to lists
    b_array = np.array(b)
    a_array = np.array(a)
    assert a_array[0] == 1.0
    a_array = a_array[1:]
    # for k in [0,.., N-1]: a_array[k] = a[k+1]
    # reverse b and a
    b_array = b_array[::-1]
    # for k in [0,.., N]: b_array[k] = b[N-k]
    a_array = a_array[::-1]
    # for k in [0,.., N-1]: a_array[k] = a[N-k]
    ## print 'reversed a_array = ', a_array
    ## print 'reversed b_array = ', b_array

    def filter_step(window_list, state_list):
        # The window size is N+1.
        # len(window_list) = N+1
        # len(state_list) = N
        # window_list is:
        # [x[m-N], x[m-N+1],...,x[m]]
        # for some m >= N.
        # if m < N: state_list is [] 
        # else: state_list is
        #     [y[m-N],,..., y[m-1]]
        ## print 'state_list', state_list
        ## print 'window_list', window_list

        if not state_list:
            # Initializing the filter
            ## print 'Initializing the filter'
            ## print 'window_list = ', window_list
            # m = N, and so:
            # window_list is:
            # [x[0], ..., x[N]]
            state_list = window_list[:-1]
            # state_list is: [x[0], ..., x[N-1]]
            # We initialize by setting y[j] = x[j]
            # So, state_list is now:
            # [y[0], ..., y[N-1]]

        # The filter has been initialized
        # window_list is:
        #   [x[m-N], x[m-N+1],...,x[m]]
        # state_list is
        #     [y[m-N],,..., y[m-1]]

        window_array = np.array(window_list)
        # window_array = [x[m-N], x[m-N+1],...,x[m]]
        # for some m
        state_array = np.array(state_list)
        # [y[m-N],..., y[m-1]]
        ## print 'state_array', state_array
        ## print 'window_array', window_array
        next_output = (np.dot(window_array, b_array) -
                       np.dot(state_array, a_array))
        # next_output is y[m]=:
        # sum over k in [0,..., N]: x[m-k]*b[k] +
        # sum over k in [1, .., N]: y[m-k]*a[k]
        # print 'next_output =', next_output
        assert not math.isinf(next_output)
        # state_list is
        #     [y[m-N],,..., y[m-1]]
        state_list.append(next_output)
        # state_list is
        #     [y[m-N],,..., y[m-1], y[m]]
        state_list = state_list[1:]
        # state_list is
        #     [y[m+1-N],..., y[m]]
        # =   [y[m'-N],..., y[m'-1]] for m'=m+1
        ## print 'state_list returned = ', state_list
        # return (next_output=y[m], state_list=[y[m-N],...,y[m]])
        return (next_output, state_list)

    return stream_func(
            inputs=input_stream,
            f_type='window',
            f=filter_step,
            num_outputs=1,
            state=[],
            window_size=window_size,
            step_size=1)
    
    
def main():
    x = Stream('x')

    fs=250
    b, a = butter_bandpass(
        lowcut=4,
        highcut=10,
        fs=fs,
        order=5)

    # Create sine wave with frequency of 8
    num_cycles = 4
    hertz_1 = 8
    hertz_2 = 16
    time = 0.25
    wavelength = 0.1
    t = np.linspace(0, 20, 5000)
    z_1 = np.sin(2*np.pi*hertz_1*t)
    z_2 = 0.5*np.sin(2*np.pi*hertz_2*t)
    z_3 = z_1+z_2
    #print 't_1', t_1
    #print 'z', z
    #x.extend(z)
    plt.plot(z_1[4000:])
    #plt.title('input')
    plt.show()
    plt.close()
    plt.plot(z_2[4000:])
    #plt.title('input')
    plt.show()
    plt.close()
    plt.plot(z_3[4000:])
    #plt.title('input')
    plt.show()
    plt.close()

    y = filter(b, a, input_stream=x)
    x.extend(z_3)
    plt.plot(y.recent[4000:y.stop])
    plt.title('output')
    plt.show()
    plt.close()

    
    
if __name__ == '__main__':
    main()

