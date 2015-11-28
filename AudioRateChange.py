'''
Created on Oct 30, 2015

@author: julian
'''
import pyaudio
import wave
import struct
import sys
from Stream import Stream, _multivalue,  _close
from Operators import stream_agent
from MakeProcess import make_process
from multiprocessing import Process, Queue


import logging

def package_into_lists(input_stream, output_stream, window_size):
    def identity(lst):
        # print "Package"
        return lst
    return stream_agent(
        inputs=input_stream, # The input is input_stream
        outputs=output_stream,
        f_type='window', # Identifies 'window' wrapper
        f=identity, # The function that is wrapped
        window_size=window_size,
        step_size=window_size)

def insert_interpolated_values(input_stream, output_stream, n):

    def interpolate(lst):
        if len(lst) < 2: return lst
        increment = (lst[1] - lst[0])/float(n)
        return_list = [lst[0]+k*increment for k in range(n)]
        return _multivalue(return_list)

    return stream_agent(
        inputs=input_stream, # The input is input_stream
        outputs=output_stream,
        f_type='window', # Identifies 'window' wrapper
        f=interpolate, # The function that is wrapped
        window_size=2,
        step_size=1)

def keep_every_nth_value(input_stream, output_stream, n):
    def drop(lst):
        # print "Drop"
        return lst[0]
    return stream_agent(
        inputs=input_stream, # The input is input_stream
        outputs=output_stream,
        f_type='window', # Identifies 'window' wrapper
        f=drop, # The function that is wrapped
        window_size=n,
        step_size=n)


def stream_to_output(input_stream, num_channels=1, \
                     sample_width=2, frame_rate=44100):
    """
    Parameters
    ----------
    py_audio: instance of PyAudio
    input_stream: Stream of audio samples
    num_channels: number of audio channels (1 or 2 for mono/stereo)
    sample_width: number of bytes per sample
    frame_rate: rate at which samples are played back (samples/second)

    """
    py_audio = pyaudio.PyAudio()
    logging.info('Preparing output audio stream')

    audio_stream = py_audio.open(format=py_audio.get_format_from_width(sample_width),
                channels=num_channels,
                rate=frame_rate,
                output=True,
                input=False)
    wf = wave.open("modified.wav", 'wb')

    wf.setsampwidth(sample_width)
    wf.setnchannels(num_channels)
    wf.setframerate(frame_rate)


    def write_samples_to_output(formatted_samples):
        # print "Play"
        audio_stream.write(formatted_samples.encode("ISO-8859-1"))
        wf.writeframes(formatted_samples.encode("ISO-8859-1"))


    stream_agent(inputs=input_stream, outputs=[], f_type='element',
                       f=write_samples_to_output)


    # need to call these when the stream is terminated - how to do this?
    #audio_stream.stop_stream()
    #audio_stream.close()

def format_audio_output(input_stream, output_stream):
    """
    Parameters
    ----------
    stream: stream of lists of shorts that need to be converted to byte data for audio output
    """

    def format_data(shorts):
        # print "Format"
        format = 'h'*len(shorts)
        packed = struct.pack(format, *shorts)
        return packed

    return stream_agent(
                       inputs=input_stream,
                       outputs=output_stream,
                       f_type='element',
                       f=format_data)


def wavfile_to_stream(filename, output_stream, chunk_size=1024, force_mono=True):
    """
    Parameters
    ----------
    filename: wav file to be opened
    output_stream: stream
    chunk_size: unit of i/o to read samples
    force_mono: boolean

    """
    # print "Read"
    wf = wave.open(filename, 'rb')

    sample_width = wf.getsampwidth()
    num_channels = wf.getnchannels()
    frame_rate = wf.getframerate()

    logging.info('Wavefile %s has %d audio channels at %d samples/sec frame rate and %d byte samples', \
             filename, num_channels, frame_rate, sample_width)


    data = wf.readframes(chunk_size)

    while data != '':
        chunk = chunk_size
        if len(data) != chunk_size*num_channels*sample_width:
            # fewer than CHUNK samples returned
            chunk = len(data)/num_channels/sample_width
        # data from readframes is a string of bytes
        if sample_width == 1:
            # 8 bit samples
            format = 'b'*num_channels*chunk
        elif sample_width == 2:
            # 16 bit samples
            format = 'h'*num_channels*chunk

        waveData = list(struct.unpack(format, data))

        # if required stream is mono, and wavefile is stereo, extract only the Left channel

        if force_mono and num_channels == 2:
            waveData = [waveData[i] for i in range(0,len(waveData),2)]

        output_stream.extend(waveData)

        data = wf.readframes(chunk_size)


def main():

    # in this example we read a wav file of audio of Angelina Jolie speaking,
    # and slow it down to half speed before playing it through the loudspeaker

    log = logging.getLogger('')
    log.setLevel(logging.INFO)

    format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)


    wav_file = 'AngelinaJolieShortExtract.wav'

    # the number of samples we will read/write at one time to the audio system
    CHUNK = 1024

    audio_input_stream = Stream('stream from file '+wav_file)

    # Make processes

    def create_audio_stream(input_streams, output_streams):
        wavfile_to_stream(wav_file, output_streams[0], chunk_size=CHUNK, force_mono=True)

        output_streams[0].append(_close)

    def shift_freq(input_streams, output_streams):

        keep_every_nth_value(input_streams[0], output_streams[0], 1)

    def chunk_stream(input_streams, output_streams):
        package_into_lists(input_streams[0], output_streams[0], CHUNK)

    def format_stream(input_streams, output_streams):
        format_audio_output(input_streams[0], output_streams[0])

    def play(input_streams, output_streams):
        stream_to_output(input_streams[0], frame_rate=22050)

    # Connections

    conn_0 = ('localhost', 8888)
    conn_1 = ('localhost', 8889)
    conn_2 = ('localhost', 8890)
    conn_3 = ('localhost', 8891)
    conn_4 = ('localhost', 8892)

    queue_1 = Queue()
    queue_2 = Queue()
    queue_3 = Queue()
    queue_4 = Queue()

    process_0 = Process(target=make_process,
                        args= (
                            [], # list of input stream names
                            ['audio_input_stream'], # list of output stream names
                            create_audio_stream, # func
                            None, # the input queue
                            [[queue_1]], # list of list of output queues
                            ))

    process_1 = Process(target=make_process,
                        args= (
                            ['audio_input_stream'], # list of input stream names
                            ['shift_frequency_stream'], # list of output stream names
                            shift_freq, # func
                            queue_1, # the input queue
                            [[queue_2]], #list of list of output queues
                            ))

    process_2 = Process(target=make_process,
                        args= (
                            ['shift_frequency_stream'], # list of input stream names
                            ['chunked_stream'], # list of output stream names
                            chunk_stream, # func
                            queue_2, # the input queue
                            [[queue_3]], #list of list of output queues
                            ))

    process_3 = Process(target=make_process,
                        args= (
                            ['chunked_stream'], # list of input stream names
                            ['formatted_stream'], # list of output stream names
                            format_stream, # func
                            queue_3, # the input queue
                            [[queue_4]], #list of list of output queues
                            ))

    process_4 = Process(target=make_process,
                        args= (
                            ['formatted_stream'], # list of input stream names
                            [], # list of output stream names
                            play, # func
                            queue_4, # the input queue
                            [], #list of list of output queues
                            ))

    #########################################
    # 3. START PROCESSES


    process_1.start()

    process_2.start()

    process_3.start()

    #time.sleep(0.1)
    process_4.start()

    #time.sleep(0.1)
    process_0.start()

    #########################################
    # 4. JOIN PROCESSES
    #time.sleep(0.1)
    process_4.join()
    process_3.join()
    process_2.join()
    #time.sleep(0.1)
    process_1.join()
    #time.sleep(0.1)
    process_0.join()

    # processing the audio: we can shift the frequency up (keep_every) or down (insert)

    #shift_frequency_stream = insert_interpolated_values(audio_input_stream, 1)
    '''
    shift_frequency_stream = keep_every_nth_value(audio_input_stream, 1)

    processed_audio_stream = shift_frequency_stream

    chunked_stream = package_into_lists(processed_audio_stream, CHUNK)
    chunked_stream.set_name('Chunked audio for output')

    formatted_stream = format_audio_output(chunked_stream)
    formatted_stream.set_name('Formatted chunked output')

    # The frame_rate should really be set to whatever the wav file is encoded at ...
    audio_output_stream = stream_to_output(py_audio, formatted_stream, frame_rate=22050)

    # create the audio stream from the wave file. We insist on a mono stream.
    wavfile_to_stream(wav_file, audio_input_stream, chunk_size=CHUNK, force_mono=True)
    '''


if __name__ == '__main__':
    main()
