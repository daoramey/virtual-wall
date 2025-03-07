import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os
data,rate=sf.read('kemar0.wav')
newfilter=np.zeros((data.shape))
print(data.shape)
'''newfilter[0,:]=1
for n in range(72):
 sf.write('kemar'+str(5*n)+'.wav',newfilter,rate)'''
