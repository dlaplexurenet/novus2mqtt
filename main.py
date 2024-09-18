import os, sys, signal
import time, datetime
import binascii, json
import argparse
import logging
import serial
import paho.mqtt.client as mqttClient

APP_NAME = "novus2mqtt"
APP_VERSION = "2022.2.1"

DEFAULT_LOG_LEVEL_STRING = "INFO"
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_SERIAL_BAUDRATE = 9600
DEFAULT_MQTT_BROKER = "mqtt"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_CLIENTID = "novus2mqtt"
DEFAULT_MQTT_BASE_PREFIX = "novus2mqtt"
DEFAULT_NOVUS_CONFIG = "./config/novus.json"
DEFAULT_MQTT_TOPICS = "./config/topics.json"
DEFAULT_HASS_DISCOVERY_SCHEME = "./config/homeassistant.json"
DEFAULT_HASS_DISCOVERY_PREFIX = "homeassistant"

SERIAL_PORT = os.getenv('SERIAL_PORT', DEFAULT_SERIAL_PORT)
SERIAL_BAUDRATE = int(os.getenv('SERIAL_BAUDRATE', DEFAULT_SERIAL_BAUDRATE))

MQTT_BROKER = os.getenv('MQTT_BROKER', DEFAULT_MQTT_BROKER)
MQTT_PORT = int(os.getenv('MQTT_PORT', DEFAULT_MQTT_PORT))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_CLIENTID = os.getenv('MQTT_CLIENTID', DEFAULT_MQTT_CLIENTID)
MQTT_BASE_PREFIX = os.getenv('MQTT_BASE_PREFIX', DEFAULT_MQTT_BASE_PREFIX)

NOVUS_CONFIG = os.getenv('NOVUS_CONFIG', DEFAULT_NOVUS_CONFIG)
MQTT_TOPICS = os.getenv('MQTT_TOPICS', DEFAULT_MQTT_TOPICS)
HASS_DISCOVERY_SCHEME = os.getenv('HASS_DISCOVERY_SCHEME', DEFAULT_HASS_DISCOVERY_SCHEME)

LOGGER = logging.getLogger(__package__)

BUS_DEV = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0xff]
BUS_CMD = [0x00, 0x80, 0x81, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88]
BUS_WRITE_AFTER_CMD = [0x84, 0x87]

#def mqtt_connect(client, userdata, flags, rc) -> None:
def mqtt_connect(client, userdata, flags, rc, properties=None) -> None:
    # Handle connection logic
    if rc == 0:
        LOGGER.info('MQTT: Connected to Broker')

        global mqtt_connected
        mqtt_connected = True
    else:
        LOGGER.info('MQTT: Connection failed')

def mqtt_on_message(client, userdata, message) -> None:
    msgTopic : str = message.topic
    msgPayload : str = str(message.payload.decode("utf-8"))

    LOGGER.info(format_log_message(tag="MQTT Message Published", topic=msgTopic, data=msgPayload))

    busMsgValue = None
    try:
        busMsgValue = [int("0x{0}".format(msgPayload[i : i + 2]), 16) for i in range(0, len(msgPayload), 2)]
    except:
        pass

    if msgTopic == f'{MQTT_BASE_PREFIX}/Set/Ventilation/Level' and msgPayload in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "0a", "0b", "0c", "0d"]: # 01..03 = Preset 1..3, 04=Boost, 05=Unoccupied, 06=Auto, 07..0d = Fan Speed 1..7
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x28, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Ventilation/OperatingMode' and msgPayload in ["00", "01", "02"]: # 01=Supply and Extract Air Mode, 02=Extract Air Mode, 03=Supply Air Mode
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x2a, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Ventilation/AutoMode' and msgPayload in ["e000", "e801", "ec01"]: # e000=Time, e801=Sensor, ec01=Joint Operation Mode with Fire Place
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x63, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Ventilation/Automatic/SensorControled/Mode' and msgPayload in ["0100", "0500"]: # 0100=Voltage, 0500=Current
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x05, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/FrostProtection/Mode' and msgPayload in ["00", "01", "02"]: # 00=Eco, 01=Sicher, 02=Feuchte WT
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x7b, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Defroster/Type' and msgPayload in ["00", "02", "03"]: # 00=None, 02=PTC-Defroster, 03=Sole-Defroster
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x7f, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Sole-Defroster/Mode' and msgPayload in ["10", "0c", "1c"]: # 10=Sole-Defroster Nicht Vorhanden, 0c=Sole-Defroster Vorhanden aber Nicht Freigeben, 1c=Sole-Defroster Vorhanden und Freigegeben
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x1e, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/GeothermalHeatExchangerFlap/Mode' and msgPayload in ["00", "04", "0c"]: # 00=EWT-Klappe Nicht Vorhanden, 04=EWT-Klappe Vorhanden aber Nicht Freigegeben, 0c=EWT-Klappe Vorhanden und Freigegeben
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x24, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/SupplementaryHeating/Mode' and msgPayload in ["00", "04", "0c"]: # 00=Nachheizung Nicht Vorhanden, 04=Nachheizung Vorhanden aber Nicht Freigegeben, 0c=Nachheizung Vorhanden und Freigegeben
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x21, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/SupplementaryHeating/Type' and msgPayload in ["00", "01", "03"]: # 00=None, 01=Elektroheizregister, 03=Warm-Wasser-Heizer
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x80, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Bypass/Mode' and msgPayload in ["73", "77", "7f"]: # 73=Bypass Nicht Vorhanden, 77=Bypass Vorhanden aber Nicht Freigegeben, 7f=Bypass Vorhanden und Freigegeben
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x1b, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Bypass/Test' and msgPayload in ["01", "02"]: # 01=Open, 02=Close
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x62, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/SummerVentilation/Mode' and msgPayload in ["f300", "7300"]: # f300=Akitv, 7300=Inactiv
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x18, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Language' and msgPayload in ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0a", "0b"]: # 00=German, 01=English, 02=French, 03=Dutch, 04=Polish, 05=Swedish, 06=Slovenian, 07=Slovakian, 08=Italian, 09=Latvian, 0a=Spanish, 0b=Czech
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x06, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/State' and msgPayload in ["00", "01"]: # 00=Standby, 01=On
        bus_write_request(bus_message(adr=[0x01, 0x00], cmd=0x85, data=[0x07, 0x00] + busMsgValue))

    elif msgTopic == f'{MQTT_BASE_PREFIX}/Set/Mem' and msgPayload == "dump":
        bus_write_request(bus_message(adr=[0x01, 0x01], cmd=0x83))

def crc16_ccitt(crc : bytes, data : list) -> bytes:
    msb = crc >> 8
    lsb = crc & 255
    for c in data:
        x = c ^ msb
        x ^= (x >> 4)
        msb = (lsb ^ (x >> 3) ^ (x << 4)) & 255
        lsb = (x ^ (x << 5)) & 255
    return (msb << 8) + lsb

def format_leading_zero(str: str) -> str:
    return '0' + str if len(str) < 2 else str

def novus_checksum(data : list) -> list:
    crc = crc16_ccitt(0, data)
    try:
        return [int(format_leading_zero(hex(crc)[-2:]), 16), int(format_leading_zero(hex(crc)[2:][:-2]), 16)]
    except:
        LOGGER.error(('Error calc crc: data={0} crc={1}'.format(data, crc)))
        pass
    return []

def novus_validate(data : list) -> bool:
    return novus_validate_checksum(data) and expected_data_length(data) == len(data[6:])

def novus_validate_checksum(data : list) -> bool:
    refCrc = data[4:6]
    crc = novus_checksum(data[0:4] + data[6:])
    return refCrc == crc

def expected_data_length(data : list) -> int:
    if data[3] >= 0x80:
        return int(hex(data[3] - 0x80), 16)
    return int(hex(data[3]), 16)

def format_log_message(data : list, tag : str=None, topic : str=None, err : str=None) -> str:
    if err is None:
        err = ''
    else:
        err =  ' error={0}'.format(err)

    if tag is None:
        tag = '-'

    if topic is None:
        topic = ''
    else:
        topic = 'topic={0} '.format(topic)

    if type(data) is str:
        return ('{tag} - {topic}msg={data}{err}'.format(tag=tag, topic=topic, data=data, err=err))
    else:
        return ('{tag} - l={len:02d} data={data}{err}'.format(tag=tag, len=len(data), data=' '.join('{:02x}'.format(x) for x in data), err=err))

def bus_read(bus: serial) -> None:
    global busWriteStack

    while bus.is_open:
        busDataFirstByte = []
        while len(busDataFirstByte) != 1:
            busDataFirstByte += bus.read()

        if busDataFirstByte[0] in [0x00, 0x01]:
            busDataDevice = []
            while len(busDataDevice) != 1:
                busDataDevice += bus.read()

            if busDataDevice[0] in BUS_DEV:
                busDataCmd = []
                while len(busDataCmd) != 1:
                    busDataCmd += bus.read()

                if busDataCmd[0] in BUS_CMD:
                    busDataLength = []
                    while len(busDataLength) != 1:
                        busDataLength += bus.read()

                    busDataChecksum = []
                    while len(busDataChecksum) != 2:
                        busDataChecksum += bus.read()

                    busData = busDataFirstByte + busDataDevice + busDataCmd + busDataLength + busDataChecksum

                    busDataLengthInt = int.from_bytes(busDataLength, byteorder='big', signed=False)

                    if busDataCmd[0] == 0x87:
                        busDataLengthInt = 3
                    
                    if busDataLengthInt > 0:
                        busDataChunk = []
                        while len(busDataChunk) != busDataLengthInt:
                            busDataChunk += bus.read()

                        busData += busDataChunk

                    skipConsume = False

                    if busDataCmd[0] == 0x00:
                        LOGGER.debug(format_log_message(tag="Clock", data=busData))
                        pass
                    elif busDataCmd[0] == 0x80:
                        skipConsume = True
                        LOGGER.debug(format_log_message(tag="Master to Device: You want to Join?", data=busData))
                    elif busDataCmd[0] == 0x81:
                        skipConsume = True
                        if busDataDevice[0] == 0x01:
                            LOGGER.debug(format_log_message(tag="Device to Master: I am in!", data=busData))
                            pass
                        else:
                            LOGGER.debug(format_log_message(tag="Master to Device: Welcome!", data=busData))
                            pass
                    elif busDataCmd[0] == 0x83:
                        LOGGER.debug(format_log_message(tag="Master to Memory: Dump!", data=busData))
                        pass
                    elif busDataCmd[0] == 0x84:
                        skipConsume = True
                        LOGGER.debug(format_log_message(tag="Device to Master: Give me a Ping!", data=busData))
                    elif busDataCmd[0] == 0x85 and busDataLengthInt == 3 and busData[6] in [0x04, 0x08, 0x0e, 0x11, 0x14, 0x17, 0x1a, 0x1d, 0x20, 0x23, 0x25, 0x44, 0x90, 0x93]:
                        LOGGER.debug(format_log_message(tag="Master to Device: Write Ping to Memory", data=busData))
                        pass
                    elif busDataCmd[0] == 0x86:
                        skipConsume = True
                        LOGGER.debug(format_log_message(tag="Device to Master: Any update for me?", data=busData))
                    elif busDataCmd[0] == 0x87:
                        skipConsume = True
                        LOGGER.debug(format_log_message(tag="Master to Device: See Checksum", data=busData))
                    elif busDataCmd[0] == 0x88:
                        skipConsume = True
                        LOGGER.debug(format_log_message(tag="Device: Checksum not Found", data=busData))
                    else: # should be only 0x85 left which are not ping
                        LOGGER.info(format_log_message(tag="Memory: Write", data=busData))
                        pass

                    if len(busWriteStack)>0 and busDataCmd[0] in BUS_WRITE_AFTER_CMD:
                        busStackData = busWriteStack.pop()
                        bus_write(busStackData)
                        busMsg = []
                        for busMsgByte in busStackData:
                            busMsg.append(int(binascii.hexlify((busMsgByte).to_bytes(2, byteorder='big')), 16))
                        if novus_validate(busMsg):
                            bus_consume(busMsg)

                    if busDataLengthInt>3 and not skipConsume:
                        try:
                            busMsg = []
                            for busMsgByte in busData:
                                busMsg.append(int(binascii.hexlify((busMsgByte).to_bytes(2, byteorder='big')), 16))

                            if novus_validate(busMsg):
                                bus_consume(busMsg)
                            else:
                                LOGGER.error(format_log_message(tag="Error: Checksum Failed", data=busMsg))
                        except Exception as err:
                            LOGGER.exception(format_log_message(tag="Error: Exception in Consume", data=busData, err=err))
                            pass
                else:
                    busDataFirstByte += busDataCmd
                    LOGGER.warning(format_log_message(tag="Skip: Unknown Command", data=busDataFirstByte))
            else:
                busDataFirstByte += busDataDevice
                LOGGER.warning(format_log_message(tag="Skip: Unknown Device or Wrong Sequence", data=busDataFirstByte))
        else:
            LOGGER.warning(format_log_message(tag="Skip: Wrong Beginning", data=busDataFirstByte))

        # time.sleep(0.1)

def bus_consume(msg: list) -> None:
    busMsgCmd = msg[2]
    busMsgData = None
    if len(msg) >= 6:
        busMsgData = msg[6:]

    if busMsgData and busMsgCmd == 0x85:
        busMemBlock = busMsgData

        busMemRegisters = []
        busMemData = []
        busMemIndex = 0

        for busMemByte in busMemBlock:
            busMemData.append(busMemByte)
            if busMemIndex+2 < len(busMemBlock) and busMemBlock[busMemIndex+2] == 0x00 and busMemBlock[busMemIndex+1] != 0x00 and len(busMemData) >= 2:
                adr = '0x{:02x}'.format(busMemData[0])
                if adr in novus_mar.keys():
                    if len(busMemData)-2 == int(novus_mar[adr]['payload']['length']):
                        busMemRegisters.append(busMemData)
                        busMemData = []
            busMemIndex += 1
        if len(busMemData) > 0:
            busMemRegisters.append(busMemData)
        busMemData = None

        for busMemData in busMemRegisters:
            adr = '0x{:02x}'.format(busMemData[0])

            if adr in novus_mar.keys():
                novus_mar_params = novus_mar[adr]

                value_type = novus_mar_params['payload']['type']
                value_topic = novus_mar_params['state']['topic']
                value_publish = novus_mar_params['state']['publish']

                value = busMemData[2:]
                if value_publish:
                    value_mqtt = '{0}'.format(' '.join('{:02x}'.format(x) for x in value))
                    converted_value_mqtt = None
                    formatted_value_mqtt = None
                    if value_type == "char":
                        converted_value_mqtt = '{0}'.format(bytes(value).decode("ASCII"))
                    elif value_type == "int":
                        value_signed = False
                        if novus_mar_params['payload']['signed']:
                            value_signed = bool(novus_mar_params['payload']['signed'])
                        value_decimals = 0
                        converted_value_mqtt = int.from_bytes(bytes(value), byteorder='little', signed=value_signed)
                        if novus_mar_params['payload']['decimals']:
                            value_decimals = int(novus_mar_params['payload']['decimals'])
                            converted_value_mqtt /= (value_decimals * 10)
                    elif value_type == "date":
                        if value[3] > 0 and value[3] > 0 and value[3] > 0:
                            converted_value_mqtt = '{0}'.format(datetime.date(int.from_bytes(bytes([value[3]]), byteorder='little', signed=False)+2000, int.from_bytes(bytes([value[2]]), byteorder='little', signed=False), int.from_bytes(bytes([value[1]]), byteorder='little', signed=False)))
                    elif value_type == "time":
                        converted_value_mqtt = '{0}'.format(datetime.time(int.from_bytes(bytes([value[2]]), byteorder='little', signed=False), int.from_bytes(bytes([value[1]]), byteorder='little', signed=False), int.from_bytes(bytes([value[0]]), byteorder='little', signed=False)))
                    elif value_type == "counter":
                        years = int.from_bytes(bytes([value[4]]), byteorder='little', signed=False)
                        days = int.from_bytes(bytes(value[2:3]), byteorder='little', signed=False)
                        hours = int.from_bytes(bytes([value[1]]), byteorder='little', signed=False)
                        minutes = int.from_bytes(bytes([value[0]]), byteorder='little', signed=False)

                        counter = 0
                        counter += years * (365*24*60*60) # Years
                        counter += days * (24*60*60) # Days
                        counter += hours * (60*60) # Hours
                        counter += minutes * (60) # Minutes
                        converted_value_mqtt = '{0}'.format(counter)

                        formatted_value_mqtt = "{0} years, {1} days, {2} hours, {3} minutes".format(years, days, hours, minutes)

                    mqtt_payload = {}
                    mqtt_payload['hex'] = value_mqtt
                    if converted_value_mqtt:
                        mqtt_payload['converted'] = converted_value_mqtt
                    elif 'class' in novus_mar_params['payload'].keys() and novus_mar_params['payload']['class'] == 'enum' and 'options' in novus_mar_params['payload'].keys():
                        if value_mqtt.replace(" ", "") in novus_mar_params['payload']['options'].keys():
                            mqtt_payload['converted'] = novus_mar_params['payload']['options'][value_mqtt.replace(" ", "")]
                    
                    if str(value_topic).startswith('memory'):
                        if int.from_bytes(bytes(value), byteorder='little', signed=False) <= 128:
                            mqtt_payload['char'] = '{0}'.format(bytes(value).decode("ASCII"))
                        mqtt_payload['int'] = int.from_bytes(bytes(value), byteorder='little', signed=True)
                        mqtt_payload['uint'] = int.from_bytes(bytes(value), byteorder='little', signed=False)
                    
                    if formatted_value_mqtt:
                        mqtt_payload['formatted'] = formatted_value_mqtt
                    elif 'unit_of_measurement' in novus_mar_params['payload'].keys():
                        mqtt_payload['formatted'] = '{0} {1}'.format(converted_value_mqtt, novus_mar_params['payload']['unit_of_measurement'])

                    mqtt.publish(f'{MQTT_BASE_PREFIX}/{value_topic}', payload=json.dumps(mqtt_payload), qos=0, retain=True)
    return True

def bus_write_request(data: list) -> None:
    global busWriteStack

    payload = bytearray(data)
    LOGGER.info(format_log_message(tag="Write Request: Queue on Stack", data=payload))
    busWriteStack.append(payload)

def bus_write(payload: list) -> None:
    LOGGER.info(format_log_message(tag="Write Request: Write from Stack to Bus", data=payload))
    bus.writelines([payload])

def bus_message(adr : list, cmd : bytes, data : list=[]) -> bytes:
    length = len(data)
    if cmd == 0x87:
        length += 0x80
    
    header = adr + [cmd] + [length]
    checksum = novus_checksum(header + data)
    
    return header + checksum + data

def signal_handler(signal, frame) -> None:
    global bus, mqtt

    bus.close()
    LOGGER.info('Bus: Disconnected')

    mqtt.publish(f'{MQTT_BASE_PREFIX}/status', payload='offline', qos=0, retain=True)
    mqtt.disconnect()
    LOGGER.info('MQTT: Disconnected')
    mqtt.loop_stop()

    LOGGER.info('App: Program exiting gracefully')
    sys.exit(0)

def get_arguments() -> argparse.Namespace:
    """Get passed-in arguments."""
    parser = argparse.ArgumentParser(
        description="Connector between Paul Novus bus and MQTT broker"
    )

    parser.add_argument(
        "-l",
        "--log-level",
        action="store",
        default=DEFAULT_LOG_LEVEL_STRING,
        help=f"The logging level (default: {DEFAULT_LOG_LEVEL_STRING})",
    )

    # MQTT
    parser.add_argument(
        "--mqtt-broker",
        action="store",
        required=True,
        type=str,
        help="The hostname or IP address of the MQTT broker",
    )
    parser.add_argument(
        "--mqtt-port",
        action="store",
        default=DEFAULT_MQTT_PORT,
        type=int,
        help=f"The port of the MQTT broker (default: {DEFAULT_MQTT_PORT})",
    )
    parser.add_argument(
        "--mqtt-username",
        action="store",
        default=None,
        type=str,
        help="The username to use with the MQTT broker (default: None)",
    )
    parser.add_argument(
        "--mqtt-password",
        action="store",
        default=None,
        type=str,
        help="The password to use with the MQTT broker (default: None)",
    )
    parser.add_argument(
        "--mqtt-base-prefix",
        action="store",
        type=str,
        help="The MQTT base prefix to publish the device's data to (default: novus2mqtt/<ID>)",
    )

    # Paul Novus
    parser.add_argument(
        "--novus-config",
        default=DEFAULT_NOVUS_CONFIG,
        help=(
            "The Paul Novus config file"
            f"(default: {DEFAULT_NOVUS_CONFIG})"
        ),
    )

    # Home Assistant MQTT Discovery
    parser.add_argument(
        "--hass-discovery",
        action="store_const",
        const=True,
        help="Publish data in the Home Assistant MQTT Discovery format",
    )
    parser.add_argument(
        "--hass-discovery-prefix",
        default=DEFAULT_HASS_DISCOVERY_PREFIX,
        help=(
            "The Home Assistant discovery prefix to use"
            f"(default: {DEFAULT_HASS_DISCOVERY_PREFIX})"
        ),
    )

    return parser.parse_args()

def main() -> None:
    """Run."""
    
    global novus_config, novus_mar, mqtt, mqtt_connected, bus, busWriteStack
    
    args = get_arguments()
    
    logging.basicConfig(
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        level=getattr(logging, args.log_level.upper()),
    )

    LOGGER.info("Starting {0} v{1} (python v{2})... ".format(APP_NAME, APP_VERSION, ".".join(map(str, sys.version_info[:3]))))
    LOGGER.debug("Using arguments: %s", args)

    mqtt_connected = False
    novus_config = None

    signal.signal(signal.SIGINT, signal_handler)

    try:
        bus = serial.Serial(
            port=SERIAL_PORT, 
            baudrate=SERIAL_BAUDRATE, 
            stopbits=serial.STOPBITS_ONE, 
            parity=serial.PARITY_MARK, 
            bytesize=serial.EIGHTBITS
        )
        
        LOGGER.info(f'Bus: Connected: {bus.name}')

        if bus.is_open:
            bus.close()
            bus.open()
        bus.reset_input_buffer
        bus.reset_output_buffer

        busWriteStack = []

        mqtt = mqttClient.Client(protocol=mqttClient.MQTTv5)
        #MQTT_CLIENTID

        if args.mqtt_username is not None and args.mqtt_password is not None:
            mqtt.username_pw_set(username=args.mqtt_username, password=args.mqtt_password)
        mqtt.on_connect = mqtt_connect
        mqtt.on_message = mqtt_on_message

        try:
            mqtt.connect(args.mqtt_broker, port=args.mqtt_port)
            mqtt.will_set(f'{MQTT_BASE_PREFIX}/status', payload='offline', qos=0, retain=True)

            mqtt.loop_start()
            
            mqtt.subscribe(f'{MQTT_BASE_PREFIX}/Set/#')

            while not mqtt_connected:
                time.sleep(1)

            with open(NOVUS_CONFIG) as json_file:
                novus_config = json.load(json_file)
            
            novus_mar = {}
            for adr in novus_config['memory_address_register']:
                novus_mar[adr['address']] = adr

            LOGGER.debug(f'MQTT: Publishing to {MQTT_BASE_PREFIX}/status: online') 
            mqtt.publish(f'{MQTT_BASE_PREFIX}/status', payload='online', qos=0, retain=True)

            app_config = {}
            app_config['version'] = APP_VERSION
            app_config['log_level'] = args.log_level.upper()
            app_config['name'] = novus_config['name']
            app_config['manufacturer'] = novus_config['manufacturer']
            app_config['model'] = novus_config['model']
            app_config['hw_version'] = novus_config['hw_version']
            mqtt.publish(f'{MQTT_BASE_PREFIX}/config', payload=json.dumps(app_config), qos=0, retain=True)

            bus_read(bus)
        except Exception as err:
            LOGGER.exception(f'Error {err}')
            
    except serial.serialutil.SerialException as err:
        LOGGER.exception(f'Bus: Can''t Connect {err}')

if __name__ == "__main__":
    main()