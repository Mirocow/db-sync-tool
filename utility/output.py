#!/usr/bin/python

from utility import mode, log


#
# GLOBALS
#

class bcolors:
    BEIGE = '\033[96m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLACK = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class subject:
    INFO = bcolors.GREEN + '[INFO]' + bcolors.ENDC
    LOCAL = bcolors.BEIGE + '[LOCAL]' + bcolors.ENDC
    TARGET = bcolors.BLUE + '[TARGET]' + bcolors.ENDC
    ORIGIN = bcolors.PURPLE + '[ORIGIN]' + bcolors.ENDC
    ERROR = bcolors.RED + '[ERROR]' + bcolors.ENDC
    WARNING = bcolors.YELLOW + '[WARNING]' + bcolors.ENDC


#
# FUNCTIONS
#

def message(header, message, do_print=True, do_log=False):

    if do_log:
        # @ToDo: Can this be done better? Dynamic functions?
        if header == subject.WARNING:
            log.get_logger().warning(message)
        elif header == subject.ERROR:
            log.get_logger().error(message)
        else:
            log.get_logger().info(message)

    if do_print:
        print(header + extend_output_by_sync_mode(header) + ' ' + message)
    else:
        return header + extend_output_by_sync_mode(header) + ' ' + message


def extend_output_by_sync_mode(header):
    _sync_mode = mode.get_sync_mode()
    if ((
                _sync_mode == mode.get_sync_modes().RECEIVER or _sync_mode == mode.get_sync_modes().PROXY) and header == subject.ORIGIN) or (
            (
                    _sync_mode == mode.get_sync_modes().SENDER or _sync_mode == mode.get_sync_modes().PROXY) and header == subject.TARGET) or (
            _sync_mode == mode.get_sync_modes().DUMP_REMOTE and (
            header == subject.ORIGIN or header == subject.TARGET)) or (
            _sync_mode == mode.get_sync_modes().IMPORT_REMOTE and (
            header == subject.ORIGIN or header == subject.TARGET)):
        return bcolors.BLACK + '[REMOTE]' + bcolors.ENDC

    if (_sync_mode == mode.get_sync_modes().SENDER and header == subject.ORIGIN) or (
            _sync_mode == mode.get_sync_modes().RECEIVER and header == subject.TARGET) or (
            _sync_mode == mode.get_sync_modes().DUMP_LOCAL and (
            header == subject.ORIGIN or header == subject.TARGET)) or (
            _sync_mode == mode.get_sync_modes().IMPORT_LOCAL and (
            header == subject.ORIGIN or header == subject.TARGET)):
        return bcolors.BLACK + '[LOCAL]' + bcolors.ENDC

    return ''


def client_to_subject(client):
    if client == mode.get_clients().ORIGIN:
        return subject.ORIGIN
    elif client == mode.get_clients().TARGET:
        return subject.TARGET


def host_to_subject(host):
    if host == mode.get_clients().ORIGIN:
        return subject.ORIGIN
    elif host == mode.get_clients().TARGET:
        return subject.TARGET


def get_bcolors():
    return bcolors


def get_subject():
    return subject
