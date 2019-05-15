# Script for Profiles with the in-situ KStat housing using the water column or sediment profiler

import time, serial, os
from datetime import datetime
import KStat_0_1_froehberg_driver  as KStat
from ms5837_30ba import MS5837_30BA
from tsys01 import TSYS01
from ezo_ec import EZO_EC
from KStat_pH import ph_potentiometry
from tic_t825_driver import TicSerial
from beep import beep

profile_id = '20190222_ProfilerTest1m_NF12'

dist = -250
steps = 50
step_size = dist/steps

ph_port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.5:1.0'
tic_port = "/dev/serial0"
voltammetry_port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.4:1.0'

# creating directory etc
vlt_dir = profile_id + '-voltammetry'
if not os.path.isdir(vlt_dir):
    os.mkdir(vlt_dir)
datafile = profile_id + '-data.csv'
logfile = profile_id + '-log.txt'

def log(message):
    t = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    l = open(logfile,"a")
    print("{}\t{}\n".format(t,message))
    l.write("{}\t{}\n".format(t,message))
    l.close()

def write_data(depth, time, vlt_file, p, t, s, pH, pH_flag):
    if not os.path.isfile(datafile):
        f = open(datafile, 'w')
        f.write('depth, time, vlt_file, p, t, s, pH, pH_flag\n')
        f.flush()
        f.close()
    f = open(datafile, 'a')
    f.write('{},{},{},{},{},{},{},{}\n'.format(depth, time, vlt_file, p, t, s, pH, pH_flag))
    f.flush()
    f.close()
    log("wrote data to {}".format(datafile))

first = True
def voltammetry(depth_file, ser2):
    params = {}
    with open("KStat_cyclic_params.txt") as f:
        for line in f:
           (key, val) = line.replace('\n', '').split(' = ')
           try:
               val = int(val)
           except:
                pass
           params[key] = val
    voltammetry_file = vlt_dir + '/' + depth_file
    ser2.read()
    KStat.abort(ser2)
    KStat.setupADC(ser2, params['ADSbuffer'], params['sample_rate'], params['PGA_gain'])
    KStat.setGain(ser2, params['iv_gain'])
    KStat.cyclicVoltammetry(ser = ser2, PGA_gain = params['PGA_gain'],
                            iv_gain = params['iv_gain'],
                            t_preconditioning1 = params['t_preconditioning1'],
                            t_preconditioning2 = params['t_preconditioning2'],
                            v_preconditioning1 = params['v_preconditioning1'],
                            v_preconditioning2 = params['v_preconditioning2'],
                            v1 = params['v1'], v2 = params['v2'],
                            start = params['start'], n_scans = params['n_scans'],
                            slope = params['slope'], sample_rate = params['sample_rate'],
                            file = voltammetry_file, plotting = True)
    KStat.idle(ser2, -900)

    return depth_file

def pressure():
    ms = MS5837_30BA(bus = 1)
    p = ms.read()['p']
    return p

def temperature():
    s = TSYS01(bus=1)
    t = s.read()
    return t

def salinity():
    ec = EZO_EC(bus=1, lowpower=False)
    s = TSYS01(bus=1)
    t = s.read()
    ec.t(t)
    s = ec.read()['sal']
    return s

def ph():
    with serial.Serial(ph_port, 9600, timeout=1) as ser:
        PGA_gain = 2
        iv_gain = "POT_GAIN_300K"
        KStat.setGain(ser, iv_gain)
        ph, mv, timeout = ph_potentiometry(ser, PGA_gain, measurement_time = 300, mode = 1)
        KStat.abort(ser)
        if timeout:
            pH_flag = 'timeout'
        else:
            pH_flag = ''
    return ph, pH_flag

mm = 831.5
baud_rate = 9600
device_number = None
port = serial.Serial(tic_port, baud_rate, timeout=0.1, write_timeout=0.1)
tic = TicSerial(port, device_number)
tic.reset()
tic.halt_and_set_position()
tic.set_step_mode(0)
tic.set_max_speed(3200000)
def move(dist):
    tic.energize()
    tic.exit_safe_start()
    position = tic.get_current_position()
    target = int(position+dist*mm)
    tic.set_target_position(target)
    while not tic.get_current_position() == target:
      #need to reset command timeout, otherwise the stepper will only run for 1s
      tic.reset_command_timeout()
      time.sleep(0.1)
    print('Position: {:.1f} mm'.format(tic.get_current_position()/mm))
    tic.deenergize()
    position = tic.get_current_position()/mm
    return position

def measurement(ser2):
    # Voltammetry
    log("start voltammetry measurement")
    try:
        depth_file = profile_id + '-' + str(depth)
        vlt_file = voltammetry(depth_file, ser2 = ser2)
        log("voltammetry measurement completed")
    except Exception as e:
        log("error running voltammetry experiment")
        log(e)
        
    # Pressure
    try:
        p = pressure()
        log("measured pressure")
    except Exception as e:
        p = ''
        log("error during pressure measurement")
        log(e)
        
    # Temperature
    try:
        t = temperature()
        log("measured temperature")
    except Exception as e:
        t = ''
        log("error during temperature measurement")
        log(e)
        
    # Salinity
    """try:
        s = salinity()
        log("measured salinity")
    except Exception as e:
        s = ''
        log("error during salinity measurement")
        log(e)"""
        
    # pH
    """try:
        log("start pH measurement")
        pH, pH_flag = ph()
        log("end pH measurement")
    except Exception as e:
        pH = ''
        log("error during pH measurement")
        log(e)
        pH_flag = 'error'"""
    #return (vlt_file, p, t, s, pH, pH_flag)
    return (vlt_file, p, t)


if __name__ == "__main__":
    
    with serial.Serial(voltammetry_port, 9600, timeout=1) as ser2:
        log('start profile {}'.format(profile_id))
        depth = tic.get_current_position()/mm
        
        for i in range(steps):

            beep(0.2,0)
            vlt_file, p, t = measurement(ser2)

            # Data output
            ts = time.time()
            write_data(depth, ts, vlt_file, p, t, 0, 0, 'not measured')
            log("data written")

            # Move Profiler
            try:
                depth = move(step_size)
                log("moved profiler")
            except Exception as e:
                log("error during profiler operation")
                log(e)
                               
        log('completed profile {}'.format(profile_id))
