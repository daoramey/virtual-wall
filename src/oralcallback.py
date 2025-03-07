import numpy as np
import time
import wave
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from sound import sound
from scipy import signal
import pyaudio
import scipy
import soundfile as sf

p = pyaudio.PyAudio()
#
def callback(in_data, frame_count, time_info, status):
    #print(len(in_data))
    #print((time_info['output_buffer_dac_time']-time_info['input_buffer_adc_time'])*48000)
    """print(frame_count)
    print(len(in_data))
    print(in_data)
    print((time_info['output_buffer_dac_time']-time_info['current_time'])*48000)
    print((time_info['current_time']-time_info['input_buffer_adc_time'])*48000)
    #print(status)
    #print(time.clock())
    input_data = np.frombuffer(in_data,dtype=np.float32)
    print(input_data)
    print('start')
    print(len(in_data))
    print(len(input_data))
    print(in_data)
    print(input_data)
    output_data = input_data.astype(np.float32).tostring()
    print((time_info['output_buffer_dac_time']-time_info['input_buffer_adc_time'])*48000)
    #print(time.time())
    print(output_data)"""
    return (in_data, pyaudio.paContinue)
#
print(p.get_default_host_api_info())
stream0 = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=48000,
                input=True,
                 #input_device_index=1,
                output=True,
                 #output_device_index=1,
                frames_per_buffer=0,
                stream_callback=callback)
#
stream0.start_stream()
while stream0.is_active():
    cmd=input('Enter q to exit...')
    if cmd =='q':
     stream0.stop_stream()
stream0.close()
p.terminate()
