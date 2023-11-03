import time
import serial
from serial.tools import list_ports


serial_port_str = ''


def find_usb_port_automatically(vp):
    # vp: vid_pid -> '1234:5678'
    vp = vp.upper()
    for p in list_ports.comports():
        info = dict({"Name": p.name,
                     "Description": p.description,
                     "Manufacturer": p.manufacturer,
                     "Hwid": p.hwid})
        if vp in info['Hwid']:
            return '/dev/' + info['Name']


class ExceptionVCP(Exception):
    pass


def tx_rx(port, cmd, exp: bytes):

    # get serial port
    sp = serial.Serial(port, 9600, timeout=.1)

    # flush stuff
    sp.readall()
    sp.flushInput()

    # send our command
    if type(cmd) is not bytes:
        cmd = cmd.encode()
    sp.write(cmd)

    # read serial bytes for a while
    ans = bytes()
    timeout_wait_ans = time.perf_counter() + 1
    while time.perf_counter() < timeout_wait_ans:
        try:
            ans += sp.readall()
            if ans == exp:
                break
        except (Exception, ):
            # when timeout
            pass

    # close serial port when out the loop
    if sp:
        sp.close()

    # check answer
    print('ans', ans)
    if ans != exp:
        raise ExceptionVCP(f'error: cmd {cmd} exp {exp} ans {ans}')
