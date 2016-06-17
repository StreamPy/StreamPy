if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func
import numpy as np
import random



def main():

    def mean_of_window(stream):

        def mean(lst, state):
            sum_window, next_value_dropped = state
            if sum_window is None:
                sum_window = sum(lst)
            else:
                sum_window = sum_window + lst[-1] - next_value_dropped
            mean = sum_window/len(lst)
            next_value_dropped = lst[0]
            state = (sum_window, next_value_dropped)
            return (mean, state)

        return stream_func(
            inputs=stream,
            f_type='window',
            f=mean,
            num_outputs=1,
            state=(None, None),
            window_size=2,
            step_size=2)


    def max_of_std(lst, state):
        a = np.array(lst).std()
        if a > state:
            state = a
            return (a, state)
        else:
            return (_no_value, state)
        

    x = Stream('x')
    # x is the input stream.


    g = partial(stream_func, f_type='window',
                f=max_of_std,
                num_outputs=1, state=0.0,
                window_size=10, step_size=10)

    y = g(x)
    z = g(y)
    means = mean_of_window(x)

    y.set_name('y')
    z.set_name('z')
    means.set_name('means')

    x.extend([random.random() for i in range(30)])
    x.print_recent()
    y.print_recent()
    z.print_recent()
    means.print_recent()


if __name__ == '__main__':
    main()
