if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from scipy.signal import butter, lfilter
import numpy as np
import matplotlib.pyplot as plt
from Stream import Stream 
from Operators import stream_func



def butter_bandpass(lowcut, highcut, fs, order=5):
    """ Returns parameters b, a for a Butterworth bandpass
    filter.
    
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

def linear_filter(lst, state):
    """
    Implements:
    a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
                        - a[1]*y[n-1] - ... - a[na]*y[n-na]
    where:
    arrays b, a are inputs and are stored in the state,
    x is the input moving window
    y is a moving window stored in the state.

    """
    b, a, y = state # see scipy.signal.lfilter
    if not a[0]:
        raise Exception()
    # reverse b (for reasons: see below)
    b = b[::-1]
    x = np.array(lst)
    # For the notes below, x[0] in our implementation is x[n-nb]
    # in scipy, .., and x[nb] in our implementation is x[n]
    # in scipy.
    # because the sliding window of length nb ranges is now
    # where the front of the window is the n-th element in the
    # stream.
 
    # From scipy.signal.lfilter notes:
    # a[0].y[n] = (b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb] -
    #         a[1]*y[n-1] + ... + a[na]*y[n-na])
    # So ensure:
    #       len(x) = len(b) = nb
    #       len(y) = len(a)-1 = na-1
    # The size of the moving window is nb and this ensures
    # len(x) == len(b)
    #
    # We store only y[n-1],... y[n-na] from the scipy notes, because
    # y[n] is computed at each step. Moreover, we reverse
    # y[n-1],...,y[n-na], i.e., y[0] in our implementation is y[n-1] in
    # the scipy notes, and y[na-1] in our implementation is y[n-na]
    # in the scipy notes.
    # So, a[1]*y[n-1] + ... + a[na]*y[n-na] in the scipy notes is
    # a[1]*y[0] +...+a[na]*y[na-1] in our notes,
    # i.e, it is sum(a[1:]*y).
    # Similarly, since we reversed b, b[0]...b[nb] in scipy is
    # b[nb],.., b[0] in our implementation, and since x[n-nb],..x[n]
    # in scipy is x[0], ..,x[nb] in our implementation:
    # b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb] in scipy is
    # sum(b*x)
     
    if np.isclose(a[0], 1.0):
        # This is the normal case.
        output = (sum(b*x) - sum(a[1:]*y))
    else:
        output = (sum(b*x) - sum(a[1:]*y))/a[0]
    # Shift y to the right and add output as the leftmost element.
    y[1:] = y[:-1]
    y[0] = output
    return (output, state)


x = Stream('x')
## z = stream_func(x, f_type='window', f=linear_filter, num_outputs=1,
##                 state=0.0, window_size=window_size, step_size=step_size)

def main():
    b, a = butter_bandpass(lowcut=0.1, highcut=5.0, fs=50, order=5)
    y = np.zeros(len(a)-1)
    state = (b, a, y)
    filename = '20110111000000.2D.OBS34.SXZ.npy'
    data_array = np.load(filename)
    print 'len(data_array)', len(data_array)
    data_array = data_array[:1000000]
    x = Stream('x')
    print 'a', a
    print 'b', b
    y = stream_func(x, f_type='window', f=linear_filter, num_outputs=1,
                    state=state, window_size=len(b), step_size=1)
    x.extend(data_array)
    y.set_name('y')
    plt.plot(y.recent[5000:y.stop])
    plt.show()
    plt.close()
    

if __name__ == '__main__':
    main()
    
    
    


    
    
