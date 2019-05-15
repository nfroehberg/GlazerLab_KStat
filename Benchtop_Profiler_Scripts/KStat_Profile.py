#https://www.pololu.com/docs/0J71/8
import time, sys, logging
import RPi.GPIO as GPIO
from serial import Serial
import KStat_0_1_froehberg_driver as KStat

def oxygen(ser, sample_rate, file, cleaning):
    print("start measurement")
    return KStat.cyclicVoltammetry(ser = ser, PGA_gain = PGA_gain,
                                   iv_gain = iv_gain, t_preconditioning1 = cleaning,
                                   t_preconditioning2 = 2, v_preconditioning1 = -900,
                                   v_preconditioning2 = -100, v1 = -1850, v2 = -100,
                                   start = -100, n_scans = 1, slope = 500, sample_rate = sample_rate,
                                   file = file, plotting = True)
        



topreed = 4
bottomreed = 27
beeppin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(topreed, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bottomreed, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(beeppin, GPIO.OUT, initial=GPIO.HIGH)
mm = 200
top = 48000
bottom = 0

def reset(ser):
    ser.write(0xB0)

def energize(ser):
    ser.write(0x85)

def deenergize(ser):
    ser.write(0x86)

def exit_safe_start(ser):
    ser.write(0x83)
    
def write32(v):
    v = v.to_bytes(4, byteorder='little')
    
    m = (((0x80 & v[0]) >> 7) +\
         ((0x80 & v[1]) >> 6) +\
         ((0x80 & v[2]) >> 5) +\
         ((0x80 & v[3]) >> 4))
    v = bytearray([vv & 0x7F for vv in v])
    return bytearray([m]) + v

def set_pos(ser, p, timeout_s=0):

    start = time.time()
    
    c = bytearray([0xE0]) + write32(p)
    ser.write(c)

    while time.time() - start < timeout_s:
        if get_pos(ser) == p:
            return True
        ser.write(c)
    return False

def get_pos(ser):
    ser.write(bytes([0xA1, 0x22, 4]))
    r = ser.readline()
    return int.from_bytes(r, byteorder='little')

def set_target_velocity(ser, v):
    c = bytearray([0xE3]) + write32(v)
    ser.write(c)

def home(ser, end='top'):
    assert end in ['top', 'bottom']

    if 'bottom' == end:
        if not GPIO.input(bottomreed):
            logging.debug('Already at limit. Moving away...')
            set_target_velocity(ser, 4000000)
            time.sleep(10)
        while GPIO.input(bottomreed):
            set_target_velocity(ser, -4000000)
            time.sleep(0.1)
        set_target_velocity(ser, 0)
    elif 'top' == end:
        if not GPIO.input(topreed):
            logging.debug('Already at limit. Moving away...')
            set_target_velocity(ser, -4000000)
            time.sleep(10)
        while GPIO.input(topreed):
            set_target_velocity(ser, 4000000)
        set_target_velocity(ser, 0)
    return True

def move(ser, dist):
    
    target = get_pos(ser) + int(dist)
    if target >= bottom and target <= top:
        while not set_pos(ser, target):
            if get_pos(ser) == target:
                position = (top - get_pos(ser))/mm
                print('Position: {} mm'.format(0-position))
                break
with Serial('/dev/ttyS0', 9600, timeout=0.2) as ser:
    with Serial('/dev/ttyACM0', 115200, timeout=1) as ser2:
    
        #prepare KStat
        ADSbuffer = 1
        Samplingrate = "1KHz"
        PGA_gain = 2
        iv_gain = "POT_GAIN_300K"
        
        KStat.setupADC(ser2, ADSbuffer, Samplingrate, PGA_gain)
            
        KStat.setGain(ser2, iv_gain)

        KStat.idle(ser2, -900)

        #prepare stepper
        exit_safe_start(ser)
        get_pos(ser)
        get_pos(ser)
        get_pos(ser)
        position = (top - get_pos(ser))/mm
        print('Position: {} mm'.format(1-position))
        last = (-1)*mm

        while True:
            usr = input("Enter distance in mm (positive = upwards, negative = downwards, 't' = top, 'b' = bottom, 'enter' = last entered value, 'h' = home, 'e' = exit:\n")
            energize(ser)
            try:
                dist = float(usr)*mm
                steps = int(input("Enter number of steps:\n"))
                cleaning = int(input("Enter duration of cleaning potential [S]:\n"))
                last = dist
                target = get_pos(ser) + dist*steps
                if target >= bottom and target <= top:
                    for i in range(steps):
                        step = get_pos(ser) + ((i + 1) * dist)
                        while not set_pos(ser, step):
                            if get_pos(ser) == target:
                                position = (top - get_pos(ser))/mm
                                print('Position: {} mm'.format(0-position))
                                break
                        
                        #measure
                        KStat.abort(ser2)
                        for i in range(3):
                            file = "{}-{}".format(position,i)
                            print(file)
                            oxygen(ser2, Samplingrate, file, cleaning)
                        KStat.idle(ser2, -900)
                else:
                    print('Target outside range')
            except:
                if usr in ['t', 'b', '']:
                    if usr == 't':
                        target = top
                    if usr == 'b':
                        target = bottom
                    if usr == '':  
                        target = get_pos(ser) + int(last)
                    while not set_pos(ser, target):
                        if get_pos(ser) == target:
                            position = (top - get_pos(ser))/mm
                            print('Position: {} mm'.format(0-position))
                            break
                elif usr == 'e':
                    sys.exit()
                elif usr == 'h':
                    home(ser, end='top')
                    get_pos(ser)
                    get_pos(ser)
                    get_pos(ser)
                    get_pos(ser)
                    get_pos(ser)
                    get_pos(ser)
                    get_pos(ser)
                    get_pos(ser)
                    top = get_pos(ser)
                    position = (top - get_pos(ser))/mm
                    print('Position: {} mm'.format(0-position))
                else:
                    print('Invalid input')
            deenergize(ser)
