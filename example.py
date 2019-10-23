#!/usr/bin/env python3
import time
from pprint import pprint
from pystiebeleltron import pystiebeleltron

UNIT = 'LWZ'
ISG_IP = '192.168.2.2'

def main():
    isg = pystiebeleltron.StiebelEltronAPI(unit=UNIT, isg_ip=ISG_IP)
    isg.update()

    result = isg.get_registers()

    for block in result:
        for rtype in block:
            for register in block[rtype]:
                value = register[1]['value']
                if 'unit' in register[1] and register[1]['unit']:
                    value = f"{value} {register[1]['unit']}"
                if 'value_raw' in register[1]:
                    value = f"{value} (RAW {register[1]['value_raw']})"
                print('{}: {}'.format(register[0], value))


    #pprint(isg.set_register('ROOM_TEMP_COOL_DAY_HC1', 22.5))
    #isg.update()
    #pprint(isg.get_register_value_formatted('ROOM_TEMP_COOL_DAY_HC1'))


if __name__ == "__main__":
    main()
