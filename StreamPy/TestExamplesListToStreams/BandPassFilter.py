from scipy.signal import butter, lfilter
import sys
import numpy as np

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

def bandpass_filter(input_array, lowcut, highcut, sample_rate, order=5):
    #fs = highcut * 2 / float(sample_rate)
    fs = 100.0
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, input_array)

def main():
    ## b, a = butter_bandpass(lowcut=0.1, highcut=5.0, fs=250, order=5)
    ## print 'b'
    ## print b
    ## print 'a'
    ## print a
    
def main(input_array_file):
    import matplotlib.pyplot as plt
    print "input file ", input_array_file
    input_array = np.load(input_array_file)
    print 'length(input_array)', len(input_array)
    input_array = input_array[:5]
    y = bandpass_filter(
        input_array=input_array,
        lowcut=1.0,
        highcut=5.0,
        #sample_rate=50, #for OBS
        sample_rate=40, # for SCSN
        order=5)

    plt.plot(y)
    plt.title("Bandpass Filter")
    plt.show()
    ## plt.savefig('Low_Pass_' + input_array_file.replace('.npy', '.png'))

    ## results_filename = 'LowPass_'+ input_array_file
    ## np.save(results_filename, y)

if __name__ == '__main__':
    ##main()
    main(sys.argv[1])
