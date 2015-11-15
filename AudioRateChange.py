'''
Created on Oct 30, 2015

@author: julian
'''
import pyaudio
import wave
import struct
import sys
from Stream import Stream, _multivalue
from Operators import stream_func
from MakeProcess import make_process


import logging

def package_into_lists(input_stream, window_size):
    def identity(lst):
        return lst
    return stream_func(
        inputs=input_stream, # The input is input_stream
        f_type='window', # Identifies 'window' wrapper
        f=identity, # The function that is wrapped
        num_outputs=1, # Returns a single stream
        window_size=window_size,
        step_size=window_size)

def insert_interpolated_values(input_stream, n):

    def interpolate(lst):
        if len(lst) < 2: return lst
        increment = (lst[1] - lst[0])/float(n)
        return_list = [lst[0]+k*increment for k in range(n)]
        return _multivalue(return_list)

    return stream_func(
        inputs=input_stream, # The input is input_stream
        f_type='window', # Identifies 'window' wrapper
        f=interpolate, # The function that is wrapped
        num_outputs=1, # Returns a single stream
        window_size=2,
        step_size=1)

def keep_every_nth_value(input_stream, n):
    def drop(lst):
        return lst[0]
    return stream_func(
        inputs=input_stream, # The input is input_stream
        f_type='window', # Identifies 'window' wrapper
        f=drop, # The function that is wrapped
        num_outputs=1, # Returns a single stream
        window_size=n,
        step_size=n)


def stream_to_output(py_audio, input_stream, num_channels=1, \
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

    logging.info('Preparing output audio stream')

    audio_stream = py_audio.open(format=py_audio.get_format_from_width(sample_width),
                channels=num_channels,
                rate=frame_rate,
                output=True,
                input=False)

    def write_samples_to_output(formatted_samples):
        audio_stream.write(formatted_samples)


    return stream_func(inputs=input_stream, f_type='element',
                       f=write_samples_to_output, num_outputs=0)


    # need to call these when the stream is terminated - how to do this?
    #audio_stream.stop_stream()
    #audio_stream.close()

def format_audio_output(stream):
    """
    Parameters
    ----------
    stream: stream of lists of shorts that need to be converted to byte data for audio output
    """

    def format_data(shorts):
        format = 'h'*len(shorts)
        packed = struct.pack(format, *shorts)
        return packed

    return stream_func(
                       inputs=stream,
                       f_type='element',
                       f=format_data,
                       num_outputs=1)


def wavfile_to_stream(filename, output_stream, chunk_size=1024, force_mono=True):
    """
    Parameters
    ----------
    filename: wav file to be opened
    output_stream: stream
    chunk_size: unit of i/o to read samples
    force_mono: boolean

    """

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

    py_audio = pyaudio.PyAudio()

    wav_file = 'AngelinaJolieShortExtract.wav'

    # the number of samples we will read/write at one time to the audio system
    CHUNK = 1024

    audio_input_stream = Stream('stream from file '+wav_file)

    # Make processes

    def create_audio_stream(input_streams, output_streams):
        wavfile_to_stream(wav_file, output_streams[0], chunk_size=CHUNK, force_mono=True)

        output_streams[0].append(_close)

    def shift_freq(input_stream, output_stream):
        output_stream = keep_every_nth_value(input_stream, 2)

    def chunk_stream(input_stream, output_stream):
        output_stream[0] = package_into_lists(input_stream[0], CHUNK)
        output_stream[0].set_name('Chunked audio for output')

    def format_stream(input_stream, output_stream):
        output_stream[0] = format_audio_output(input_stream[0])
        output_stream[0].set_name('Formatted chunked output')

    def play(input_streams, output_streams):
        output_streams[0] = stream_to_output(py_audio, input_streams[0], frame_rate=22050)

    process_0 = Process(target=make_process,
                        args= (
                            [], # list of input stream names
                            ['audio_input_stream'], # list of output stream names
                            create_audio_stream, # func
                            None, # the input queue
                            [[conn_1]], # list of list of output queues
                            conn_0[0],
                            conn_0[1]
                            ))

    # This process receives simple_stream from process_0.
    # It sends double_stream to process_2.
    # It receives messages on queue_1 and sends messages to queue_2.
    process_1 = Process(target=make_process,
                        args= (
                            ['audio_input_stream'], # list of input stream names
                            ['shift_frequency_stream'], # list of output stream names
                            shift_freq, # func
                            queue_1, # the input queue
                            [[conn_2]], #list of list of output queues
                            conn_1[0],
                            conn_1[1]
                            ))

    process_2 = Process(target=make_process,
                        args= (
                            ['shift_frequency_stream'], # list of input stream names
                            ['chunked_stream'], # list of output stream names
                            chunk_stream, # func
                            queue_1, # the input queue
                            [[conn_2]], #list of list of output queues
                            conn_1[0],
                            conn_1[1]
                            ))

    process_3 = Process(target=make_process,
                        args= (
                            ['chunked_stream'], # list of input stream names
                            ['formatted_stream'], # list of output stream names
                            format_stream, # func
                            queue_1, # the input queue
                            [[conn_2]], #list of list of output queues
                            conn_1[0],
                            conn_1[1]
                            ))

    process_4 = Process(target=make_process,
                        args= (
                            ['formatted_stream'], # list of input stream names
                            [], # list of output stream names
                            play, # func
                            queue_1, # the input queue
                            [[conn_2]], #list of list of output queues
                            conn_1[0],
                            conn_1[1]
                            ))

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

    py_audio.terminate()

if __name__ == '__main__':
    main()
