# This file is part of the pyBinSim project.
#
# Copyright (c) 2017 A. Neidhardt, F. Klein, N. Knoop, T. Köllmer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" Module contains main loop and configuration of pyBinSim """
import logging
import time
import numpy as np
import pyaudio

from pybinsim2.convolver import ConvolverFFTW
from pybinsim2.filterstorage import FilterStorage
from pybinsim2.osc_receiver import OscReceiver
from pybinsim2.pose import Pose
from pybinsim2.soundhandler import SoundHandler


def parse_boolean(any_value):

    if type(any_value) == bool:
        return any_value

    # str -> bool
    if any_value == 'True':
        return True
    if any_value == 'False':
        return False

    return None



class BinSimConfig(object):
    def __init__(self):

        self.log = logging.getLogger("pybinsim2.BinSimConfig")

        # Default Configuration
        self.configurationDict = {'blockSize': 128,
                                  'filterSize': 16384,
                                  'filterList': 'brirs/filter_list_kemar5.txt',
                                  'enableCrossfading': False,
                                  'useHeadphoneFilter': False,
                                  'loudnessFactor': float(1),
                                  'maxChannels': 8,
                                  'samplingRate': 48000,
                                  'loopSound': False,
                                  }

    def read_from_file(self, filepath):
        config = open(filepath, 'r')

        for line in config:
            line_content = str.split(line)
            key = line_content[0]
            value = line_content[1]

            if key in self.configurationDict:
                config_value_type = type(self.configurationDict[key])

                if config_value_type is bool:
                    # evaluate 'False' to False
                    boolean_config = parse_boolean(value)

                    if boolean_config is None:
                        self.log.warning("Cannot convert {} to bool. (key: {}".format(value, key))

                    self.configurationDict[key] = boolean_config
                else:
                    # use type(str) - ctors of int, float, ...
                    self.configurationDict[key] = config_value_type(value)

            else:
                self.log.warning('Entry ' + key + ' is unknown')

    def get(self, setting):
        return self.configurationDict[setting]



class BinSim(object):
    """
    Main pyBinSim2 program logic
    """

    def __init__(self, config_file):
        self.log = logging.getLogger("pybinsim2.BinSim")
        self.log.info("BinSim: init")

        # Read Configuration File
        self.config = BinSimConfig()
        self.config.read_from_file(config_file)

        self.current_config = self.config
        self.nChannels = self.current_config.get('maxChannels')
        self.sampleRate = self.current_config.get('samplingRate')
        self.blockSize = self.current_config.get('blockSize')
        self.result = None
        self.block = None
        self.stream = None

        self.convolverWorkers = []
        self.convolverHP, self.convolvers, self.filterStorage, self.oscReceiver  = self.initialize_pybinsim()


        self.p = pyaudio.PyAudio()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cleanup()

    def stream_start(self):
        self.log.info("BinSim: stream_start")
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=2,
                                  rate=self.sampleRate,
                                  input=True,
                                  output=True,
                                  #input_device_index=1,
                                  #output_device_index=1,
                                  frames_per_buffer=self.blockSize,
                                  stream_callback=audio_callback(self))
        self.stream.start_stream()

        while self.stream.is_active():
            time.sleep(1)
            cmd=input('Enter q to exit...')
            if cmd =='q':
             self.stream.stop_stream()

    def initialize_pybinsim(self):
        self.result = np.empty([self.config.get('blockSize'), 2], np.dtype(np.float32))  # ------- result(256,2)-------#
        self.block = np.empty([self.config.get('maxChannels'), self.config.get('blockSize')], np.dtype(np.float32))  # ------- block(maxchannel,256)-------#
        # Create FilterStorage
        filterStorage = FilterStorage(self.config.get('filterSize'), self.config.get('blockSize'),
                                      self.config.get('filterList'))
        # Start an oscReceiver
        oscReceiver = OscReceiver()
        oscReceiver.start_listening()
        time.sleep(1)

        # Create N convolvers depending on the number of wav channels
        self.log.info('Number of Channels: ' + str(self.config.get('maxChannels')))
        convolvers = [None] * self.config.get('maxChannels')
        for n in range(self.config.get('maxChannels')):
            convolvers[n] = ConvolverFFTW(self.config.get('filterSize'), self.config.get('blockSize'), False)

        # HP Equalization convolver
        convolverHP = None
        if self.config.get('useHeadphoneFilter'):
            convolverHP = ConvolverFFTW(self.config.get('filterSize'), self.config.get('blockSize'), True)
            hpfilter = filterStorage.get_headphone_filter()
            convolverHP.setIR(hpfilter, False)

        return convolverHP, convolvers, filterStorage, oscReceiver  # soundHandler

    def close(self):
        self.log.info("BinSim: close")
        self.stream_close()
        self.p.terminate()

    def stream_close(self):
        self.log.info("BinSim: stream_close")
        self.stream.stop_stream()
        self.stream.close()

    def __cleanup(self):
        # Close everything when BinSim is finished
        self.filterStorage.close()
        self.close()

        self.oscReceiver.close()

        for n in range(self.config.get('maxChannels')):
            self.convolvers[n].close()

        if self.config.get('useHeadphoneFilter'):
            if self.convolverHP:
                self.convolverHP.close()


def audio_callback(binsim):
    """ Wrapper for callback to hand over custom data """
    assert isinstance(binsim, BinSim)

    def callback(in_data, frame_count, time_info, status):
        #current_soundfile_list = binsim.oscReceiver.get_sound_file_list()
        in_data = np.fromstring(in_data, dtype=np.float32)
        audio_data = np.empty((2,binsim.blockSize))
        audio_data[0,:]=in_data[::2]
        audio_data[1,:]=in_data[1::2]
        print(in_data.shape)
        # Get sound block.  return buffer_content
        binsim.block = audio_data
        # Update Filters and run each convolver with the current block n=0
        for n in range(binsim.nChannels):
            # Get new Filter
            if binsim.oscReceiver.is_filter_update_necessary(n):
                  filterValueList = binsim.oscReceiver.get_current_values(n)
                  filter = binsim.filterStorage.get_filter(Pose.from_filterValueList(filterValueList))
                  binsim.convolvers[n].setIR(filter, callback.config.get('enableCrossfading'))
            left, right = binsim.convolvers[n].process(binsim.block[n,:])

            # Sum results from all convolvers
            if n == 0:

                binsim.result[:, 0] = left
                binsim.result[:, 1] = right
            else:
                binsim.result[:, 0] = np.add(binsim.result[:, 0],left)
                binsim.result[:, 1] = np.add(binsim.result[:, 1],right)

        # Finally apply Headphone Filter
        if callback.config.get('useHeadphoneFilter'):
            binsim.result[:, 0], binsim.result[:, 1] = binsim.convolverHP.process(binsim.result)

        # Scale data
        binsim.result = np.multiply(binsim.result,callback.config.get('loudnessFactor'))
        if np.max(np.abs(binsim.result))>1:
            binsim.log.warn('Clipping occurred: Adjust loudnessFactor!')


        return (binsim.result[:frame_count].tostring(), pyaudio.paContinue)

    callback.config = binsim.config

    return callback
