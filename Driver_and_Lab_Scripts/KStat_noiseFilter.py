# Script designed to remove AC noise (60Hz and higher harmonics) from KStat voltammetric data
# FIlter: IIR notch
# Nico Fröhberg nfroeh@hawaii.edu

from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal

#read list of data files
files = glob('*.csv')

for file in files:
    #read files
    name = file[0:file.index('.csv')]
    dat = pd.read_csv(file, engine='python')

    #extracting sampling rate from parameter file
    parafile = name + '-parameters.txt'
    params = pd.read_csv(parafile, delim_whitespace=True, engine='python', names=['0','1','2','3'], index_col=0)
    samplerate = params['2']['Samplerate']
    Samplingrates = {"2.5Hz":2.5, "5Hz":5.0, "10Hz":10.0, "15Hz":15.0,
                         "25Hz":25.0, "30Hz":30.0, "50Hz":50.0, "60Hz":60.0,
                         "100Hz":100.0, "500Hz":500.0, "1KHz":1000.0, "2KHz":2000.0,
                         "3.75KHz":3750.0, "7.5KHz":7500.0, "15KHz":1500.0, "30KHz":30000.0}
    samplerate = Samplingrates[samplerate]

    #constructing IIR notch filters
    fs = samplerate   # Sample frequency (Hz)
    f0 = 60.0  # Frequency to be removed from signal (Hz)
    Q = 2.0  # Quality factor
    # Design notch filter
    b, a = signal.iirnotch(f0, Q, fs)
    c, d = signal.iirnotch(f0*2, Q, fs)
    e, f = signal.iirnotch(f0*4, Q, fs)
    g, h = signal.iirnotch(f0*5, Q, fs)
    i, j = signal.iirnotch(f0*6, Q, fs)
    
    #apply filters
    yf1 = signal.filtfilt(b,a,dat.current) #60Hz filter
    yf2 = signal.filtfilt(c,d,yf1) #120Hz filter
    yf3 = signal.filtfilt(e,f,yf2) #240Hz filter
    yf4 = signal.filtfilt(g,h,yf3) #300Hz filter
    yf5 = signal.filtfilt(i,j,yf4) #360Hz filter

    #generate output plots
    fig = plt.figure(figsize=(6,4))
    plt.plot(dat.potential, yf5*-1000000000,'b')
    plt.gca().invert_xaxis()
    plt.xlabel('Potential [mV]')
    plt.ylabel('Current [nA]')
    plt.xlim(0,-1900)
    plt.title(name)
    fig.savefig(('filtered/'+name+'.png'), dpi=150)
    plt.close(fig)

    #save filtered data
    dat['current_filtered'] = yf5
    dat.to_csv((name+'.csv'), index=False)
    print('Filtered {}'.format(name))
