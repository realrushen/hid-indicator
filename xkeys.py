import logging

import hid

XKEYS_VENDOR_ID = 0x05F3
XKEYS_PRODUCT_ID = 0x0405

logger = logging.getLogger(__name__)


def open_xkeys():
    try:
        device = hid.device(XKEYS_VENDOR_ID, XKEYS_PRODUCT_ID)
        device.set_nonblocking(1)
        logger.info('found device %s', device)
        return device
    except IOError as ex:
        logger.debug(ex)
        logger.info('Device not found')


def parse_report(report):
    keys_states = []
    keys_bytes = bytearray(report[3:7])
    for byte in keys_bytes:
        binary_string = "{:08b}".format(byte)
        keys_states.extend(reversed(binary_string[2:]))
    return keys_states


def read_xkeys(device):
    try:
        report = device.read(33)
        if not report:
            return [0] * 24
        keys_states = parse_report(report)
        return keys_states
    except IOError as ex:
        logger.error(ex)


def device_connected():
    for device_dict in hid.enumerate():
        vid = device_dict['vendor_id']
        pid = device_dict['product_id']
        if vid == XKEYS_VENDOR_ID and pid == XKEYS_PRODUCT_ID:
            return True
    return False
