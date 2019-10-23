"""
Connection to a Stiebel Eltron ModBus API.
"""
import logging
import os
from pymodbus.client.sync import ModbusTcpClient
from pprint import pprint

"""
See API details:
https://www.stiebel-eltron.de/content/dam/ste/de/de/home/services/Downloadlisten/ISG%20Modbus_Stiebel_Bedienungsanleitung.pdf

Types of data:

Data | Value      | Multiplier  | Multiplier  | Signed | Step   | Step
type | range      | for reading | for writing |        | size 1 | size 5
-----|------------|-------------|-------------|--------|--------|-------
2    | -3276.8 to | 0.1         | 10          | Yes    | 0.1    | 0.5
     |  3276.7    |             |             |        |        |
6    | 0 to 65535 | 1           | 1           | No     | 1      | 5
7    | -327.68 to | 0.01        | 100         | Yes    | 0.01   | 0.05
     |  327.67    |             |             |        |        |
8    | 0 to 255   | 1           | 1           | No     | 1      | 5
"""

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOGLEVEL', 'DEBUG'))

REGISTERS = {
    # Integral ventilation units
    'LWZ': {
        'ERRORS': {
            'N/A':                 32768,
            'SENSOR_LEAD_MISSING': -60, # Sensor lead is missing or disconnected
            'SHORTCUT':            -50, # Short circuit of the sensor lead
        },
        # Block 1 System values (Read input register)
        'BLOCKS': [
            {
                'INPUT': [
                    # HC = Heating Circuit
                    ('ACTUAL_ROOM_TEMPERATURE_HC1',      {'addr':  1, 'type': 2, 'unit': '°C',}),
                    ('SET_ROOM_TEMPERATURE_HC1',         {'addr':  2, 'type': 2, 'unit': '°C',}),
                    ('ACTUAL_ROOM_TEMPERATURE_HC2',      {'addr':  4, 'type': 2, 'unit': '°C',}),
                    ('SET_ROOM_TEMPERATURE_HC2',         {'addr':  5, 'type': 2, 'unit': '°C',}),
                    ('RELATIVE_HUMIDITY_HC1',            {'addr':  3, 'type': 2, 'unit': '%',}),
                    ('RELATIVE_HUMIDITY_HC2',            {'addr':  6, 'type': 2, 'unit': '%',}),
                    ('OUTSIDE_TEMPERATURE',              {'addr':  7, 'type': 2, 'unit': '°C',}),
                    ('ACTUAL_VALUE_HC1',                 {'addr':  8, 'type': 2, 'unit': '°C',}),
                    ('SET_VALUE_HC1',                    {'addr':  9, 'type': 2, 'unit': '°C',}),
                    ('ACTUAL_VALUE_HC2',                 {'addr': 10, 'type': 2, 'unit': '°C',}),
                    ('SET_VALUE_HC2',                    {'addr': 11, 'type': 2, 'unit': '°C',}),
                    ('FLOW_TEMPERATURE',                 {'addr': 12, 'type': 2, 'unit': '°C',}),
                    ('RETURN_TEMPERATURE',               {'addr': 13, 'type': 2, 'unit': '°C',}),
                    ('PRESSURE_HEATING_CIRCUIT',         {'addr': 14, 'type': 2, 'unit': 'bar',}),
                    ('FLOW_RATE',                        {'addr': 15, 'type': 2, 'unit': 'l/min',}),
                    ('ACTUAL_DHW_TEMPERATURE',           {'addr': 16, 'type': 2, 'unit': '°C',}),
                    ('SET_DHW_TEMPERATURE',              {'addr': 17, 'type': 2, 'unit': '°C',}),
                    ('VENTILATION_AIR_ACTUAL_FAN_SPEED', {'addr': 18, 'type': 6, 'unit': 'Hz',}),
                    ('VENTILATION_AIR_SET_FLOW_RATE',    {'addr': 19, 'type': 6, 'unit': 'm³/h',}),
                    ('EXTRACT_AIR_ACTUAL_FAN_SPEED',     {'addr': 20, 'type': 6, 'unit': 'Hz',}),
                    ('EXTRACT_AIR_SET_FLOW_RATE',        {'addr': 21, 'type': 6, 'unit': 'm³/h',}),
                    ('EXTRACT_AIR_HUMIDITY',             {'addr': 22, 'type': 6, 'unit': '%',}),
                    ('EXTRACT_AIR_TEMPERATURE',          {'addr': 23, 'type': 2, 'unit': '°C',}),
                    ('EXTRACT_AIR_DEW_POINT',            {'addr': 24, 'type': 2, 'unit': '°C',}),
                    ('DEW_POINT_TEMPERATURE_HC1',        {'addr': 25, 'type': 2, 'unit': '°C',}),
                    ('DEW_POINT_TEMPERATURE_HC2',        {'addr': 26, 'type': 2, 'unit': '°C',}),
                    ('COLLECTOR_TEMPERATURE',            {'addr': 27, 'type': 2, 'unit': '°C',}),
                    ('HOT_GAS_TEMPERATURE',              {'addr': 28, 'type': 2, 'unit': '°C',}),
                    ('HIGH_PRESSURE',                    {'addr': 29, 'type': 7, 'unit': 'bar',}),
                    ('LOW_PRESSURE',                     {'addr': 30, 'type': 7, 'unit': 'bar',}),
                    ('COMPRESSOR_STARTS',                {'addr': 31, 'type': 6}),
                    ('COMPRESSOR_SPEED',                 {'addr': 32, 'type': 2, 'unit': 'Hz',}),
                    ('MIXED_WATER_AMOUNT',               {'addr': 33, 'type': 6, 'unit': 'l',}),
                ],
            },
            # Block 2 System parameters (Read/write holding register)
            {
                'HOLDING': [
                    ('OPERATING_MODE', {
                        'addr':  1001,
                        'type':  8,
                        'code':  {
                            'AUTOMATIC':           11,
                            'STANDBY':             1,
                            'DAY MODE':            3,
                            'SETBACK MODE':        4,
                            'DHW':                 5,
                            'MANUAL MODE':         14,
                            'EMERGENCY OPERATION': 0,
                        },
                    }),
                    ('ROOM_TEMP_HEAT_DAY_HC1',   {'addr': 1002, 'type': 2, 'unit': '°C',}),
                    ('ROOM_TEMP_HEAT_NIGHT_HC1', {'addr': 1003, 'type': 2, 'unit': '°C',}),
                    ('MANUAL_SET_TEMP_HC1',      {'addr': 1004, 'type': 2, 'unit': '°C',}),
                    ('ROOM_TEMP_HEAT_DAY_HC2',   {'addr': 1005, 'type': 2, 'unit': '°C',}),
                    ('ROOM_TEMP_HEAT_NIGHT_HC2', {'addr': 1006, 'type': 2, 'unit': '°C',}),
                    ('MANUAL_SET_TEAMP_HC2',     {'addr': 1007, 'type': 2, 'unit': '°C',}),
                    ('GRADIENT_HC1',             {'addr': 1008, 'type': 7, 'unit': '°C',}),
                    ('LOW_END_HC1',              {'addr': 1009, 'type': 2, 'unit': '°C',}),
                    ('GRADIENT_HC2',             {'addr': 1010, 'type': 7, 'unit': '°C',}),
                    ('LOW_END_HC2',              {'addr': 1011, 'type': 2, 'unit': '°C',}),
                    ('DHW_TEMP_SET_DAY',         {'addr': 1012, 'type': 2, 'unit': '°C',}),
                    ('DHW_TEMP_SET_NIGHT',       {'addr': 1013, 'type': 2, 'unit': '°C',}),
                    ('DHW_TEMP_SET_MANUAL',      {'addr': 1014, 'type': 2, 'unit': '°C',}),
                    ('MWM_SET_DAY',              {'addr': 1015, 'type': 6, 'unit': 'l',}),
                    ('MWM_SET_NIGHT',            {'addr': 1016, 'type': 6, 'unit': 'l',}),
                    ('MWM_SET_MANUAL',           {'addr': 1017, 'type': 6, 'unit': 'l',}),
                    ('DAY_STAGE',                {'addr': 1018, 'type': 6}),
                    ('NIGHT_STAGE',              {'addr': 1019, 'type': 6}),
                    ('PARTY_STAGE',              {'addr': 1020, 'type': 6}),
                    ('MANUAL_STAGE',             {'addr': 1021, 'type': 6}),
                    ('ROOM_TEMP_COOL_DAY_HC1',   {'addr': 1022, 'type': 2, 'unit': '°C',}),
                    ('ROOM_TEMP_COOL_NIGHT_HC1', {'addr': 1023, 'type': 2, 'unit': '°C',}),
                    ('ROOM_TEMP_COOL_DAY_HC2',   {'addr': 1024, 'type': 2, 'unit': '°C',}),
                    ('ROOM_TEMP_COOL_NIGHT_HC2', {'addr': 1025, 'type': 2, 'unit': '°C',}),
                    ('RESET', {
                        'addr':  1026,
                        'type':  6,
                        'code':  {
                            'OFF': 0,
                            'ON':  1,
                        },
                    }),
                    ('RESTART_ISG', {
                        'addr':  1027,
                        'type':  6,
                        'code':  {
                            'OFF':   0,
                            'RESET': 1,
                            'MENU':  2,
                        },
                    }),
                ],
            },
            # Block 3 System status (Read input register)
            {
                'INPUT': [
                    ('OPERATING_STATUS', {
                        'addr':  2001,
                        'type':  6,
                        'code':  {
                            'SWITCHING_PROGRAM_ENABLED': (1 << 0),
                            'COMPRESSOR':                (1 << 1),
                            'HEATING':                   (1 << 2),
                            'COOLING':                   (1 << 3),
                            'DHW':                       (1 << 4),
                            'ELECTRIC_REHEATING':        (1 << 5),
                            'SERVICE':                   (1 << 6),
                            'POWER-OFF':                 (1 << 7),
                            'FILTER':                    (1 << 8),
                            'VENTILATION':               (1 << 9),
                            'HEATING_CIRCUIT_PUMP':      (1 << 10),
                            'EVAPORATOR_DEFROST':        (1 << 11),
                            'FILTER_EXTRACT_AIR':        (1 << 12),
                            'FILTER_VENTILATION_AIR':    (1 << 13),
                            'HEAT-UP_PROGRAM':           (1 << 14),
                        },
                    }),
                    ('FAULT_STATUS', {
                        'addr':  2002,
                        'type':  6,
                        'code':  {
                            'NO_FAULT': 0,
                            'FAULT':    1,
                        }
                    }),
                    ('BUS_STATUS', {
                        'addr':  2003,
                        'type':  6,
                        'code':  {
                            'STATUS OK':       0,
                            'STATUS ERROR':   -1,
                            'ERROR-PASSIVE':  -2,
                            'BUS-OFF':        -3,
                            'PHYSICAL-ERROR': -4,
                        },
                    }),
                    ('DEFROST_INITIATED', {
                        'addr':  2004,
                        'type':  6,
                        'code':  {
                            'OFF':       0,
                            'INITIATED': 1,
                        },
                    }),
                    ('OPERATING_STATUS-2', {
                        'addr':  2005,
                        'type':  6,
                        'code':  {
                            'SUMMER_MODE_ACTIVE':         (1 << 0),
                            'OVEN/FIREPLACE_MODE_ACTIVE': (1 << 1),
                        },
                    }),
                ],
            },
            # Block 4 Energy data (Read input register)
            {
                'INPUT': [
                    ('HEAT_METER_HEATING_DAY',             {'addr': 3001, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_HEATING_TOTAL_kWh',       {'addr': 3002, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_HEATING_TOTAL_MWh',       {'addr': 3003, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_DHW_DAY',                 {'addr': 3004, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_DHW_TOTAL_kWh',           {'addr': 3005, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_DHW_TOTAL_MWh',           {'addr': 3006, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_BOOST_HEATING_TOTAL_kWh', {'addr': 3007, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_BOOST_HEATING_TOTAL_MWh', {'addr': 3008, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_BOOST_DHW_TOTAL_kWh',     {'addr': 3009, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_BOOST_DHW_TOTAL_MWh',     {'addr': 3010, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_RECOVERY_DAY',            {'addr': 3011, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_RECOVERY_TOTAL_kWh',      {'addr': 3012, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_RECOVERY_TOTAL_MWh',      {'addr': 3013, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_SOLAR_HEATING_DAY',       {'addr': 3014, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_SOLAR_HEATING_TOTAL_kWh', {'addr': 3015, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_SOLAR_HEATING_TOTAL_MWh', {'addr': 3016, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_SOLAR_DHW_DAY',           {'addr': 3017, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_SOLAR_DHW_TOTAL_kWh',     {'addr': 3018, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_SOLAR_DHW_TOTAL_MWh',     {'addr': 3019, 'type': 6, 'unit': 'MWh',}),
                    ('HEAT_METER_COOLING_TOTAL_kWh',       {'addr': 3020, 'type': 6, 'unit': 'kWh',}),
                    ('HEAT_METER_COOLING_TOTAL_MWh',       {'addr': 3021, 'type': 6, 'unit': 'MWh',}),
                    ('POWER_METER_HEATING_DAY',            {'addr': 3022, 'type': 6, 'unit': 'kWh',}),
                    ('POWER_METER_HEATING_TOTAL_kWh',      {'addr': 3023, 'type': 6, 'unit': 'kWh',}),
                    ('POWER_METER_HEATING_TOTAL_MWh',      {'addr': 3024, 'type': 6, 'unit': 'MWh',}),
                    ('POWER_METER_DHW_DAY',                {'addr': 3025, 'type': 6, 'unit': 'kWh',}),
                    ('POWER_METER_DHW_TOTAL_kWh',          {'addr': 3026, 'type': 6, 'unit': 'kWh',}),
                    ('POWER_METER_DHW_TOTAL_MWh',          {'addr': 3027, 'type': 6, 'unit': 'MWh',}),
                    ('TIMER_COMPRESSOR_HEATING',           {'addr': 3028, 'type': 6, 'unit': 'h',}),
                    ('TIMER_COMPRESSOR_COOLING',           {'addr': 3029, 'type': 6, 'unit': 'h',}),
                    ('TIMER_COMPRESSOR_DHW',               {'addr': 3030, 'type': 6, 'unit': 'h',}),
                    ('TIMER_BOOSTER_HEATING',              {'addr': 3031, 'type': 6, 'unit': 'h',}),
                    ('TIMER_BOOSTER_DHW',                  {'addr': 3032, 'type': 6, 'unit': 'h',}),
                ],
            },
            # Block 5 Energy management settings (Read/write holding register)
            {
                'HOLDING': [
                    ('EM_SGREADY_SWITCH', {
                        'addr':  4001,
                        'type':  6,
                        'code':  {
                            'OFF':  0,
                            'ON': 1,
                        },
                    }),
                    ('EM_SGREADY_INPUT_1', {
                        'addr':  4002,
                        'type':  6,
                        'code':  {
                            'OFF': 0,
                            'ON':  1,
                        },
                    }),
                    ('EM_SGREADY_INPUT_2', {
                        'addr':  4003,
                        'type':  6,
                        'code':  {
                            'OFF': 0,
                            'ON':  1,
                        },
                    }),
                ],
            },
            # Block 6 Energy management and system information (Read input register)
            {
                'INPUT': [
                    ('EM_SGREADY_OPERATING_MODE', {
                        'addr':  5001,
                        'type':  6,
                        'code':  {
                            'REDUCED':   1,
                            'STANDARD':  2,
                            'INCREASED': 3,
                            'MAXIMIZED': 4,
                        },
                    }),
                    ('CONTROLLER_ID', {
                        'addr':  5002,
                        'type':  6,
                        'code':  {
                            'LWZ 303/403 Integral/SOL; LWA 403; LWZ 304/404 Trend; LWZ 304/404 Flex; LWZ Smart; LWZ 604 Air; LWZ 5 S Plus/Trend/Smart': 103,
                            'LWZ 304/404 SOL; LWZ 504; LWZ 5/8 CS Premium': 104,
                            'WPM 3':     390,
                            'WPM 3i':    391,
                            'WPMsystem': 449,
                        },
                    }),
                ],
            },
        ],
    },
    # TODO: Add WPM register tables
    'WPM': {},
}

class StiebelEltronAPI():
    """Stiebel Eltron API"""


    def __init__(self, unit, isg_ip, update_on_read=False):
        """Initialize Stiebel Eltron communication"""

        if unit not in REGISTERS:
            raise Exception("No registers found for unit '{}'! Supported: {}".format(unit, ', '.join(REGISTERS)))
        self._unit = unit

        self._client = ModbusTcpClient(
            host=isg_ip,
            port=502,
            timeout=20
        )
        self._client.connect()

        self._slave = 1
        self._update_on_read = update_on_read
        self._results = []


    def __del__(self):
        """Stop Stiebel Eltron communication"""
        self._client.close()


    def update(self):
        """Request current values from heat pump"""
        ret = False
        try:
            for block_cnt, block in enumerate(REGISTERS[self._unit]['BLOCKS'], start=1):
                logger.info("Processing block #%s", block_cnt)
                for rtype in ('INPUT', 'HOLDING'):
                    if rtype not in block:
                        continue
                    address = block[rtype][0][1]['addr'] - 1 # Unsure about the -1, but hey..
                    count = len(block[rtype])
                    results = None
                    if rtype == 'INPUT':
                        results = self._client.read_input_registers(
                            unit=self._slave,
                            address=address,
                            count=count,
                        ).registers
                    if rtype == 'HOLDING':
                        results = self._client.read_holding_registers(
                            unit=self._slave,
                            address=address,
                            count=count,
                        ).registers
                    if results and len(results) == count:
                        for idx, result in enumerate(results):
                            item = block[rtype][idx][1]
                            item['value_raw'] = result
                            is_error = False
                            for (err_name, err_code) in REGISTERS[self._unit]['ERRORS'].items():
                                if result == err_code:
                                    is_error = True
                                    result = err_name
                            if not is_error:
                                if item['type'] == 2:
                                    result = round(result * 0.1, 1)
                                if item['type'] == 7:
                                    result = round(result * 0.01, 1)
                                if 'code' in item:
                                    coded = []
                                    for c in item['code'].keys():
                                        if result == item['code'][c]:
                                            coded = [c]
                                            break
                                        if result & item['code'][c]:
                                            coded.append(c)
                                    result = coded
                            item['value'] = result
                    else:
                        logger.warning("Inconsistent register/result amounts: %s/%s", count, len(results))
            ret = True
        except AttributeError:
            # The unit does not reply reliably
            logger.exception("Modbus read failed")

        return ret


    def get_registers(self):
        """Returns all registers for selected heat pump unit"""
        return REGISTERS[self._unit]['BLOCKS']


    def _find_register(self, name, block_type=None):
        """Returns a single register by name. block_type enforces a filter"""
        register = None

        for my_block in REGISTERS[self._unit]['BLOCKS']:
            block_types = my_block.keys()
            if block_type:
                if block_type in block_types:
                    block_types = [block_type]
                else:
                    continue
            for my_register_set in [ my_block[my_block_type] for my_block_type in block_types ]:
                for my_register in my_register_set:
                    if my_register[0] == name:
                        register = my_register
                        break

        return register


    def get_register(self, name):
        """Return a single register by name"""
        return self._find_register(name)


    def get_register_value_formatted(self, name):
        """Return formatted value of a single register by name"""
        register = self._find_register(name)
        value = None
        if 'value' in register[1]:
            value = register[1]['value']
        if value is not None and 'unit' in register[1]:
            value = f"{value} {register[1]['unit']}"
        return value


    def set_register(self, name, value):
        """Set value for a register by name"""
        # Lookup holding register
        register = self._find_register(name, block_type='HOLDING')
        if register is None:
            raise Exception("Register not found or not HOLDING register!")

        # Apply type factor
        if register[1]['type'] == 2:
            value = round(value * 10)
        if register[1]['type'] == 7:
            value = round(value * 100)
        
        # Sanity check if code is available
        if 'code' in register[1].keys() and value not in register[1]['code'].values():
            raise Exception("Value not supported!")

        # Set register
        pprint(self._client.write_register(
            unit=self._slave,
            address=(register[1]['addr'] - 1), # Unsure about the -1, but hey..
            value=value
        ))