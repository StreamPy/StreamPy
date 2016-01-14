from Stream import Stream, _no_value, _multivalue
from Agent import Agent
from examples_element_wrapper import print_stream
from Operators import assert_is_list_of_streams_or_None, assert_is_list_of_streams
from collections import namedtuple

OutOfOrder = namedtuple('OutOfOrder', ['current_timestamp', 'previous_timestamp', 'value'])

def add_heartbeat_to_stream(
        input_stream, output_stream, time_stream, delay, call_streams=None):
    assert isinstance(input_stream, Stream)
    assert isinstance(output_stream, Stream)
    assert isinstance(time_stream, Stream)
    assert (isinstance(delay, int) or isinstance(delay, float))
    assert_is_list_of_streams_or_None(call_streams)

    def transition(in_lists, last_time):
        # in_lists[0] is the data in_list
        # in_lists[1] is the time in_list
        output = list()
        # data_list is the list of the data tuples: (time, value)
        data_list = in_lists[0].list[in_lists[0].start:in_lists[0].stop]
        # time_list is the list of times that arrived on time_stream
        time_list = in_lists[1].list[in_lists[1].start:in_lists[1].stop]
    
        #######################################
        #    Process the list of data items.  #   
        #######################################
        # Each data item is a tuple or list
        # where its 0-th value is a timestamp
        if data_list:
            # Sort, in place, the data list by timestamp.
            print 'data_list', data_list
            data_list.sort(key=lambda tup: tup[0])
            # data_list[0][0] is the earliest timestamp in
            # data_list. If the earliest timestamp is at least
            # last_time then all the timestamps in data_list are
            # at least last_time. So put the entire data list 
            # into the output stream and set last_time to the 
            # latest timestamp (i.e., data_list[-1][0]) in
            # data_list.
            if data_list[0][0] >= last_time:
                output.extend(data_list)
                last_time = data_list[-1][0]
            else:
                # If some timestamps are earlier than last_time
                # then place of OutOfOrder objects in the output
                # stream. If a timestamp is at or after last_time
                # then the corresponding item is in time order;
                # so put the item into the output stream.
                for data_item in data_list:
                    if data_item[0] < last_time:
                        output.append(
                            OutOfOrder(data_item[0], last_time, data_item))
                    else:
                        output.append(data_item)
                # last_time must be greater than or equal to
                # the latest timestamp in data_list.
                last_time = max(last_time, data_list[-1][0])

        # All the items in data_list have been processed. So
        # the agent has read up to the very end of the list,
        # i.e., to in_lists[0].stop.
        data_start_value = in_lists[0].stop
        # FINISHED PROCESSING DATA LIST
        

        #######################################
        #    Process the time list            #   
        #######################################
        if time_list:
            # The latest time in time_list is time_list[-1].
            # If no element has arrived in the data list
            # with timestamp in the interval
            # [time_list[-1] - delay , last_time] then
            # no element with a timestamp in this interval
            # is likely to arrive in the future because the
            # (expected) maximum delay for an element to get
            # to this agent is delay.
            # Indicate that there is no non-Null element in
            # this interval by appending:
            # (time_list[-1] - delay, None) to the output stream.
            if time_list[-1] - delay > last_time:
                last_time = time_list[-1] - delay
                output.append((last_time, None))
                
        time_start_value = in_lists[1].stop
        # FINISHED PROCESSING TIME_LIST

        # Finished transition()
        return ([output], last_time,
                [data_start_value, time_start_value])
    

    # Create agent
    last_time = -1
    return Agent([input_stream, time_stream],
                 [output_stream],
                 transition, last_time, call_streams)

def main():
    input_stream = Stream('input')
    output_stream = Stream('output')
    time_stream = Stream('time_stream')
    delay = 10

    print_stream(input_stream)
    print_stream(output_stream)
    print_stream(time_stream)

    add_heartbeat_to_stream(
        input_stream, output_stream, time_stream, delay)

    input_stream.extend([(5, 'A'), (10, 'B'), (30, 'C')])
    time_stream.extend([50, 55])

    input_stream.extend([(50, 'A'), (58, 'B'), (61, 'C')])
    time_stream.extend([70, 80, 100])

    input_stream.extend([(80, 'A'), (85, 'B'), (93, 'C')])
    time_stream.extend([120])

if __name__ == '__main__':
    main()
    
    

        

                    
    
