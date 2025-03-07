import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os
data,rate = sf.read('obrir136.wav')
plt.figure(1)
plt.plot(data[:,0])
plt.show()
