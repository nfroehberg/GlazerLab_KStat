# Script for pH calibration using the KStat potentiostat
# Nico Froehberg 2019, nico.froehberg@gmx.de
# generates ph_cal.txt that can be used for normal measurements
# pH electrode needs to be connected to WShield and RE connectors
# insert electrode into buffer solution and enter pH value
# measurements will run until stabilized

from KStat_pH import ph_potentiometry
from serial import Serial
from KStat_0_1_froehberg_driver import *
from scipy.stats import linregress

with Serial('/dev/ttyACM1', 9600, timeout=1) as ser:
    PGA_gain = 2
    iv_gain = "POT_GAIN_300K"
        
    setGain(ser, iv_gain)
    buffers = []
    voltage = []   
    while True:
        usr = input('Enter pH value of buffer solution, "f" to finish calibration, "e" to exit:\n')
        try:
            ph = float(usr)
        except:
            if usr == "e":
                abort(ser)
                sys.exit()
            elif usr == "f":    
                slope, intercept, r_value, p_value, std_err = linregress(voltage, buffers)
                print("Calibration complete")
                print("Slope: {:.4f}, Intercept: {:.4f}, R2: {:.5f}".format(slope,intercept,r_value))
                f = open('ph_cal.txt','w')
                f.write('{}\n{}\n{}'.format(slope,intercept,r_value))
                f.close()
                abort(ser)
                sys.exit()
            else:
                print("Invalid input, you failed, try again!")
                continue
        buffers.append(ph)
        voltage.append(ph_potentiometry(ser, PGA_gain, measurement_time = 300, mode = 1)[1])
        abort(ser)
