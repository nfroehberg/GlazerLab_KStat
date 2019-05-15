# Test Script to live display potential

from KStat_0_1_driver import *
from serial import Serial
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

def potentiometry(ser, PGA_gain, measurement_time = 0, mode = 1):
    #function for potentiometry experiment.
    #sampling rate is forced to 10 Hz because line by line readout is required for potentiometry (fast sampling can max out the serial buffer)
    #measurement time in s, if 0 will run until abort signal
    #Mode: 0 for OCP (WE is connected)/1 for potentiometry (WE input disconnected)
    setupADC(ser, ADSbuffer = 1, Samplingrate = "500Hz", PGA_gain = PGA_gain)

    commands = []
    commands.append('EP')
    commands.append(str(measurement_time))
    commands.append(str(mode))
    commands.append('\n')
    
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))

    return catchPotentiometry(ser, PGA_gain)
    
def catchPotentiometry(ser, PGA_gain):
    i = 0
    voltage = []
    t = []
    while True:
        
        line = ser.read(5000)
        lines = []
        pattern = re.compile(b'(B\n[\s\S]{8}\n*)|(S\n)|(@DONE\n)')
        for x in re.finditer(pattern, line):
            lines.append(x.group())
        for l in lines:
            try:
                s, ms, v = struct.unpack('<xxHHix', l)
                v = ADCtomV(v, PGA_gain)
                voltage.append(v)
                t.append(s + ms/1000)
            except:
                pass
        if t[-1] > 10:
            t_plot = t[-10000:-1]
            voltage_plot = voltage[-10000:-1]
        else:
            t_plot = t
            voltage_plot = voltage
        plt.clf()
        plt.plot(t_plot,voltage_plot)
        plt.draw()
        plt.pause(0.00000001)



if __name__ == "__main__":        
   #change serial port to where the KStat is connected
    with Serial('COM3', 9600, timeout=1) as ser:
        abort(ser)
        PGA_gain = 2
        iv_gain = "POT_GAIN_300K"
        setGain(ser, iv_gain)
        
        potentiometry(ser, PGA_gain, measurement_time = 300, mode = 1)
        abort(ser)



