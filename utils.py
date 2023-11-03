import csv
import time
import serial


SERIAL_PORT = '/dev/ttyUSB0'


def find_usb_port_automatically(vp):
    # vp: vid_pid -> '1234:5678'
    vp = vp.upper()
    for p in serial.tools.list_ports.comports():
        info = dict({"Name": p.name,
                     "Description": p.description,
                     "Manufacturer": p.manufacturer,
                     "Hwid": p.hwid})
        if vp in info['Hwid']:
            return '/dev/' + info['Name']


class ExceptionVCP(Exception):
    pass


def tx_rx(cmd, exp: bytes):

    # get serial port
    sp = serial.Serial(SERIAL_PORT, 9600, timeout=.1)

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


def main():
    
    # output off
    tx_rx('SOUT0\r', b'OK\r')

    # set ABC normal mode
    tx_rx('SABC3\r', b'OK\r')

    # set voltage 5 V and 1 A
    v = '0500'
    c = '0100'
    assert len(v) == 4
    assert len(c) == 4
    s = 'SETD3{}{}\r'.format(v,c)
    tx_rx(s, b'OK\rOK\r')

    # output on
    tx_rx('SOUT1\r', b'OK\r')


if __name__ == '__main__':
    main()
