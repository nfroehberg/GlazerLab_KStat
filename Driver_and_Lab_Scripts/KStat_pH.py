# Script for pH measurement using potentiometry with the KStat potentiostat
# Nico Froehberg 2019, nico.froehberg@gmx.de
# Requires calibration file (ph_cal.txt) that contains slope, intercept and
# r value in the first three lines and the python driver for the KStat in the same folder
# calibration can be done using KStat_pH_cal.py
# pH electrode needs to be connected to WShield and RE connectors

from serial import Serial
import sys, time
from KStat_0_1_driver import *
from scipy.stats import linregress
from numpy import mean, std

def ph_potentiometry(ser, PGA_gain, measurement_time = 0, mode = 1):
    #function for potentiometry experiment.
    #sampling rate is forced to 5 Hz because line by line readout is required for potentiometry (fast sampling can max out the serial buffer)
    #measurement time in s, if 0 will run until abort signal
    #Mode: 0 for OCP (WE is connected)/1 for potentiometry (WE input disconnected)
    setupADC(ser, ADSbuffer = 1, Samplingrate = "5Hz", PGA_gain = PGA_gain)

    commands = []
    commands.append('EP')
    commands.append(str(measurement_time))
    commands.append(str(mode))
    commands.append('\r\n')
    
    sendCommand(ser, bytes(" ".join(commands), encoding='ascii'))

    return catch_ph_potentiometry(ser, PGA_gain)

def catch_ph_potentiometry(ser, PGA_gain):
    i = 0
    voltage = []
    t = []
    pH = []
    #importing calibration data, if file is not found, set to zero
    try:
        cal = open("ph_cal.txt",'r')
        cal_l = cal.read().splitlines()
        cal.close()
        cal_slope = float(cal_l[0])
        cal_intercept = float(cal_l[1])
        cal_r_value = float(cal_l[2])
    except:
        print("Can't find calibration file")
        cal_slope = 0
        cal_intercept = 0
        cal_r_value = 0
        
    #set start time for timeout
    start_time = time.time()
    while True:
        line = ser.readline()
        if line == b'@DONE\n':
            print('Experiment complete')
            break
        elif line == b'B\n':
            pass
        else:
            try:
                #extract data
                s, ms, v = struct.unpack('<HHix', line)
                
                v = ADCtomV(v, PGA_gain)
                ph = cal_slope*v + cal_intercept
                voltage.append(v)
                pH.append(ph)
                t.append(s+(ms/1000))

                #determine slope to find stable measurement
                if len(voltage) >= 20:
                    slope, intercept, r_value, p_value, std_err = linregress(t[-11:-1], pH[-11:-1])
                    dev = std(pH[-11:-1])
                    print('Potential: {:.1f} mV, pH: {:5.3f}, standard deviation: {:.3f}, slope: {}'.format(v,ph,dev,slope))
                    timeout = time.time()-start_time > 90

                    #if slope is close to zero, measurement is done
                    #if not stable after 90s, take measurement anyways and set timeout flag
                    if -1e-04 < slope < 1e-04 or timeout:
                        if not timeout:
                            print("Measurement complete.")
                        else:
                            print("Measurement timed out.")
                        return (mean(pH[-11:-1]), dev, mean(voltage[-11:-1]), timeout)
                else:
                    print('Potential: {:.1f} mV, pH: {:.3f}'.format(v,ph))
            except:
                pass
                #print("Could not read line:\n{}".format(line))
            
if __name__ == "__main__":        
   #change serial port to where the KStat is connected
    with Serial('COM3', 9600, timeout=1) as ser:
        PGA_gain = 2
        iv_gain = "POT_GAIN_300K"
        setGain(ser, iv_gain)
        
        ph, dev, mv, timeout = ph_potentiometry(ser, PGA_gain, measurement_time = 300, mode = 1)
        abort(ser)
        print("pH: {:.4f}".format(ph))


