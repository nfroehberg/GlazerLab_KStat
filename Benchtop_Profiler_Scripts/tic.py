import serial, time
from tic_t825_driver import TicSerial

steps_per_thread = 880
threads_per_inch = 24
mm_per_inch = 25.4
mm = (threads_per_inch * steps_per_thread)/mm_per_inch
print(mm)

# Choose the serial port name.
port_name = "/dev/serial0"
 
# Choose the baud rate (bits per second).  This must match the baud rate in
# the Tic's serial settings.
baud_rate = 9600
 
# Change this to a number between 0 and 127 that matches the device number of
# your Tic if there are multiple serial devices on the line and you want to
# use the Pololu Protocol.
device_number = None
 
port = serial.Serial(port_name, baud_rate, timeout=0.1, write_timeout=0.1)
 
tic = TicSerial(port, device_number)

tic.reset()
tic.energize()
tic.halt_and_set_position()
tic.set_step_mode(0)
tic.set_max_speed(3200000)
position = tic.get_current_position()
print("Current position is {:.1f} mm.".format(position/mm))
target = int(1*mm)
print("Setting target position to {:.1f} mm.".format(target/mm));
tic.exit_safe_start()
tic.set_target_position(target)
while not tic.get_current_position() == target:
  #need to reset command timeout, otherwise the stepper will only run for 1s
  tic.reset_command_timeout()
  print('Position: {:.1f} mm'.format(tic.get_current_position()/mm))
  time.sleep(0.1)
print('Position: {:.1f} mm'.format(tic.get_current_position()/mm))
tic.deenergize()
