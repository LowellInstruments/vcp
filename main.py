import time
import serial


SERIAL_PORT = '/dev/ttyUSB0'


class ExceptionVCP(Exception):
    pass


def check(b: bool):
    if not b:
        raise ExceptionVCP(f'bad answer {b}')


def tx_rx(cmd, exp: bytes):

    # conversion
    if type(cmd) is not bytes:
        cmd = cmd.encode()

    # get serial port
    sp = serial.Serial(SERIAL_PORT, 9600, timeout=1)

    # flush stuff
    sp.readall()
    sp.flushInput()

    # send our command
    sp.write(cmd)

    # wait to read some serial bytes
    ans = bytes()
    sp.timeout = .2
    till = 1
    while 1:
        if time.perf_counter() > till:
            break
        ans += sp.readall()
    if sp:
        sp.close()

    # check answer
    if ans != exp:
        raise ExceptionVCP('error: cmd {cmd} exp {exp} ans {ans}')


def main():

    # output off
    tx_rx('GETC', 'whatever')

    # choose preset 3
    tx_rx('GETC', 'whatever')

    # set voltage current preset 3
    tx_rx('GETC', 'whatever')

    # output on
    tx_rx('GETC', 'whatever')
