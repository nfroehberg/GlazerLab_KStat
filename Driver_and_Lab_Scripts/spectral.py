# Test Script for spectral analysis to determine frequencies of background noise

import pandas as pd
import matplotlib.pyplot as plt
from spectrum import Periodogram

file = pd.read_csv('0.0-0.csv', engine='python', names=['Current', 'Potential'], skiprows=1)
dat = file.Current.tolist()

p = Periodogram(dat, sampling=1000)
print('Periodogram constructed')
#p.run()
print('Periodogram run')

p.plot(marker='o')
plt.show()

