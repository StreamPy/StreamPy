from Stream import Stream
import time
import random
from examples_element_wrapper import print_stream


def source_stream(
        output_stream, number_of_values, time_period,
        func, **kwargs):  
    """
    Periodically appends a value to output_stream. The values appended
    are obtained by calling the function func and passing it keyword
    arguments.

    If number_of_values is non-negative, then it is the maximum number
    of values inserted into output_stream. If number_of_values is
    negative then values are appended to output_stream forever.

    If time_period is 0 then number_of_values must be non-negative; in
    this case all the values are appended to output_stream when
    source_stream is called. 
    

    Parameters
    ----------
    output_stream: Stream
       (Could also be a list.)
       The stream to which values are appended.
       (Note: Appending messages to a list forever will cause memory
        overflow.) 
    number_of_values: int
    time_period: int or float, nonnegative
       The time between successive appends to output_stream.
    func: function
       The return value of this function is appended to output_stream.
       
    """
    if number_of_values >= 0:
        if not time_period:
            # Append all number_of_values values immediately.
            for _ in range(number_of_values):
                output_stream.append(func(**kwargs))
        else:
            # Wait for time_period between successive outputs
            for _ in range(number_of_values):
                output_stream.append(func(**kwargs))
                time.sleep(time_period)
    else:
        # number_of_values < 0
        if time_period <= 1:
            raise ValueError(
                'number_of_values < 0 and time_period < 1')
        while True:
            # Append values to output_stream forever.
            output_stream.append(func(**kwargs))
            time.sleep(time_period)

def main():
    # Examples of source_stream

    # Create a stream s and give it the name 'random integers'.
    s = Stream('random integers')
    # Create a stream r and give it the name 'random Gaussian'.
    r = Stream('random Gaussian')
    # Create an agent to print stream s. This agent is discussed later. 
    print_stream(s)
    # Create an agent to print stream r.
    print_stream(r)
    
    # Periodically append random integers to stream s.
    # Note: the parameters of random.randint are a, b where the value
    # returned by randint(a, b) is a random integer uniformly
    # distributed between a and b.
    source_stream(
        output_stream=s,
        number_of_values=3,
        time_period=1,
        func=random.randint,
        a=0,
        b=100)

    # Periodically append Gaussian random numbers to stream r.
    # Note: the parameters of random.gauss are mu, sigma where the value
    # returned by gauss(mu, sigma) is a random float with a normal
    # distribution with mean, mu, and standard deviation, sigma.
    source_stream(
        output_stream=r,
        number_of_values=5,
        time_period=0,
        func=random.gauss,
        mu=0,
        sigma=1)

    # This example shows that output_stream could also be a
    # list. (Note: Appending values to a list forever will cause memory
    # overflow.) 
    lst = list()
    source_stream(
        output_stream=lst,
        number_of_values=3,
        time_period=2,
        func=random.randint,
        a=0,
        b=100)
    print 'list of random integers = ', lst

    # This example, adds values to a stream forever. Use commands from
    # your terminal to stop this program.
    # Create a stream s and give it the name 'random integers'.
    u = Stream('random integers for ever')
    # Create an agent to print stream u.
    print_stream(u)
    
    # Periodically append random integers to stream s.
    # Append values forever (since number_of_values is negative).
    source_stream(
        output_stream=u,
        number_of_values=-1,
        time_period=3,
        func=random.randint,
        a=0,
        b=100)
    


    
    

    

if __name__ == '__main__':
    main()
        
        
    
