"""
    PyAudio
    This program refers to receive Bytes input Stram from microphone
    then play them back immediately.
    in addition to above function in this project producing binaral simulation based on input Oral
    Stram also must be solved...
    
    This is the callback (non-blocking) version.
    author  wang shuang
    """
import sys
import numpy as np
from scipy import signal
from scipy import fftpack
import wave
import threading
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as line

import pyaudio
import time



CHANNELS = 1
RATE = 44100
#blockSize = 128
CHUNK =256
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"


# pyaudio
p = pyaudio.PyAudio()
q = queue.Queue()

def callback(in_data, frame_count, time_info, status):
    global ad_rdy_ev
    
    q.put(in_data)
    ad_rdy_ev.set()
    if counter <= 0:
        return (None,pyaudio.paComplete)
    else:
        return (None,pyaudio.paContinue)


stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                frames_per_buffer=CHUNK,
                stream_callback=callback)

#if Recording:


print("Start Recording")
stream.start_stream()
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
#processing block

window = signal.hamming(CHUNK)

def read_audio_thead(q,stream,frames,ad_rdy_ev):
    global rt_data
    global fft_data
    
    while stream.is_active():
        ad_rdy_ev.wait(timeout=1000)
        if not q.empty():
            #process audio data here
            data=q.get()
            while not q.empty():
                q.get()
            rt_data = np.frombuffer(data,np.dtype('<i2'))
            rt_data = rt_data * window
            fft_temp_data=fftpack.fft(rt_data,rt_data.size,overwrite_x=True)
            fft_data=np.abs(fft_temp_data)[0:fft_temp_data.size/2+1]
                #if Recording :
            frames.append(data)
        ad_rdy_ev.clear()

ad_rdy_ev=threading.Event()

t=threading.Thread(target=read_audio_thead,args=(q,stream,frames,ad_rdy_ev))

t.daemon=True
t.start()

plt.show()

stream.stop_stream()
stream.close()

p.terminate()

print("* done recording")
    #if Recording:
wf.writeframes(b''.join(frames))
wf.close()





