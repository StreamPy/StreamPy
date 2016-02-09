from Stream import Stream, StreamArray, _multivalue 
from Operators import wf
from examples_element_wrapper import print_stream
import numpy as np
from scipy.signal import butter, filtfilt, lfilter
import matplotlib.pyplot as plt


def butter_bandpass(lowcut, highcut, fs, order):
    """ You can make a butter_bandpass_filter using
    either:
    y = lfilter(b, a, data)
    or
    y = filtfilt(b, a, data)
    where data is a NumPy array.
    filtfilt() has linear phase.

    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_lowpass(highcut, fs, order):
    """ You can make a butter_lowpass_filter using
    either:
    y = lfilter(b, a, data)
    or
    y = filtfilt(b, a, data)
    where data is a NumPy array.

    """
    nyq = 0.5 * fs
    high = highcut / nyq
    b, a = butter(order, high, btype='low')
    return b, a


## def func(window, drop_start, b, a):
##     y = filtfilt(b, a, window)[drop_start: drop_start+len(window)]
##     return _multivalue(y)

def stream_bandpass_filter_windowing(
        in_stream, out_stream, filter_type,
        drop_start, drop_end, output_size,
        b, a):
    
    def func(window, drop_start, b, a):
        y = filter_type(b, a, window)[drop_start: drop_start+len(window)]
        return _multivalue(y)

    window_size = drop_start + output_size + drop_end
    step_size = output_size
    wf(in_stream, out_stream, func, window_size, step_size,
       drop_start=drop_start, b=b, a=a)

def main():
    in_stream = StreamArray('in_stream')
    out_stream = StreamArray('out_stream')

    drop_start = 800
    drop_end = 800
    output_size = 4000
    fs = 50

    b, a = butter_bandpass(
        lowcut=0.05, highcut=2.0, fs=fs, order=2)

    stream_bandpass_filter_windowing(
        in_stream, out_stream, filtfilt,
        drop_start, drop_end, output_size,
        b, a)
    
    t = np.linspace(0, 200, 10001)
    x = np.sin(2*np.pi*t)
    x2 = np.sin(2*np.pi*10*t)
    z = x + x2
    fs = 50

    in_stream.extend(z)
    gap = fs*8
    
    for i in range(8):
        plt.plot(out_stream.recent[1000*i+drop_start:1000*i+drop_start + gap], 'r', x[1000*i:1000*i + gap], 'b')
        plt.show()
        plt.close()

    return

if __name__ == '__main__':
    main()
