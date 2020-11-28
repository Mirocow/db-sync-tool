#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import getpass
from db_sync_tool.utility import log, parser, mode, helper, output

#
# GLOBALS
#

config = {}
option = {
    'verbose': False,
    'mute': False,
    'use_origin_ssh_key': False,
    'use_target_ssh_key': False,
    'keep_dump': False,
    'dump_name': '',
    'import': '',
    'link_hosts': '',
    'default_origin_dump_dir': True,
    'default_target_dump_dir': True,
    'check_dump': True,
    'is_same_client': False,
    'config_file_path': None,
    'ssh_password': {
        'origin': None,
        'target': None
    }
}

#
# DEFAULTS
#

default_local_sync_path = '/tmp/'


#
# FUNCTIONS
#

def check_target_configuration():
    """
    Checking target database configuration
    :return:
    """
    parser.get_database_configuration(mode.Client.TARGET)


def get_configuration(host_config):
    """
    Checking configuration information by file or dictionary
    :param host_config: Dictionary
    :return:
    """
    global config

    if option['config_file_path'] is None and host_config == {}:
        sys.exit(
            output.message(
                output.Subject.ERROR,
                f'Configuration is missing',
                False
            )
        )

    if not option['config_file_path'] is None:
        if os.path.isfile(option['config_file_path']):
            with open(option['config_file_path'], 'r') as read_file:
                config = json.load(read_file)
                output.message(
                    output.Subject.LOCAL,
                    'Loading host configuration',
                    True
                )

                check_options()
        else:
            sys.exit(
                output.message(
                    output.Subject.ERROR,
                    f'Local configuration not found: {option["config_file_path"]}',
                    False
                )
            )

    if host_config:
        config = host_config

    log.get_logger().info('Starting db_sync_tool')
    if option['config_file_path']:
        output.message(
            output.Subject.INFO,
            'Configuration: ' + option['config_file_path'],
            True,
            True
        )


def check_options():
    """
    Checking configuration provided file
    :return:
    """
    if 'dump_dir' in config['origin']:
        option['default_origin_dump_dir'] = False

    if 'dump_dir' in config['target']:
        option['default_target_dump_dir'] = False

    if 'check_dump' in config:
        option['check_dump'] = config['check_dump']

    link_configuration_with_hosts()
    mode.check_sync_mode()
    check_authorization(mode.Client.ORIGIN)
    check_authorization(mode.Client.TARGET)


def check_authorization(client):
    """
    Checking arguments and fill options array
    :param client: String
    :return:
    """
    # only need authorization if client is remote
    if mode.is_remote(client):
        # Workaround if no authorization is needed
        if (mode.get_sync_mode() == mode.SyncMode.DUMP_REMOTE and client == mode.Client.TARGET) or (
                mode.get_sync_mode() == mode.SyncMode.DUMP_LOCAL and client == mode.Client.ORIGIN) or (
                mode.get_sync_mode() == mode.SyncMode.IMPORT_REMOTE and client == mode.Client.ORIGIN):
            return

        # ssh key authorization
        if 'ssh_key' in config[client]:
            _ssh_key = config[client]['ssh_key']
            if os.path.isfile(_ssh_key):
                option[f'use_{client}_ssh_key'] = True
            else:
                sys.exit(
                    output.message(
                        output.Subject.ERROR,
                        f'SSH {client} private key not found: {_ssh_key}',
                        False
                    )
                )
        elif 'password' in config[client]:
            config[client]['password'] = config[client]['password']
        else:
            # user input authorization
            config[client]['password'] = get_password_by_user(client)

        if mode.get_sync_mode() == mode.SyncMode.DUMP_REMOTE and client == mode.Client.ORIGIN and 'password' in config[mode.Client.ORIGIN]:
            config[mode.Client.TARGET]['password'] = config[mode.Client.ORIGIN]['password']


def get_password_by_user(client):
    """
    Getting password by user input
    :param client: String
    :return: String password
    """
    _password = getpass.getpass(
        output.message(
            output.Subject.INFO,
            'SSH password ' + helper.get_ssh_host_name(client, True) + ': ',
            False
        )
    )

    while _password.strip() == '':
        output.message(
            output.Subject.WARNING,
            'Password seems to be empty. Please enter a valid password.',
            True
        )

        _password = getpass.getpass(
            output.message(
                output.Subject.INFO,
                'SSH password ' + helper.get_ssh_host_name(client, True) + ': ',
                False
            )
        )

    return _password


def check_args_options(config_file=None,
                       verbose=False,
                       mute=False,
                       import_file=None,
                       dump_name=None,
                       keep_dump=None,
                       host_file=None):
    """
    Checking arguments and fill options array
    :param config_file:
    :param verbose:
    :param mute:
    :param import_file:
    :param dump_name:
    :param keep_dump:
    :param host_file:
    :return:
    """
    global option
    global default_local_sync_path

    if not config_file is None:
        option['config_file_path'] = config_file

    if not verbose is None:
        option['verbose'] = verbose

    if not mute is None:
        option['mute'] = mute

    if not import_file is None:
        option['import'] = import_file

    if not dump_name is None:
        option['dump_name'] = dump_name

    if not host_file is None:
        option['link_hosts'] = host_file

    if not keep_dump is None:
        default_local_sync_path = keep_dump

        # Adding trailing slash if necessary
        if default_local_sync_path[-1] != '/':
            default_local_sync_path += '/'

        option['keep_dump'] = True
        output.message(
            output.Subject.INFO,
            '"Keep dump" option chosen',
            True
        )


def link_configuration_with_hosts():
    """
    Merging the hosts definition with the given configuration file
    :return:
    """
    if ('link' in config['origin'] or 'link' in config['target']) and option['link_hosts'] == '':
        # Try to find default hosts.json file in same directory
        sys.exit(
            output.message(
                output.Subject.ERROR,
                f'Missing hosts file for linking hosts with configuration. '
                f'Use the "-o" / "--hosts" argument to define the filepath for the hosts file, when using a link parameter within the configuration.',
                False
            )
        )

    if option['link_hosts'] != '':
        if os.path.isfile(option['link_hosts']):
            with open(option['link_hosts'], 'r') as read_file:
                _hosts = json.load(read_file)
                output.message(
                    output.Subject.INFO,
                    'Linking configuration with hosts',
                    True
                )
                if 'link' in config['origin']:
                    _host_name = str(config['origin']['link']).replace('@','')
                    if _host_name in _hosts:
                        config['origin'] = {**config['origin'], **_hosts[_host_name]}

                if 'link' in config['target']:
                    _host_name = str(config['target']['link']).replace('@','')
                    if _host_name in _hosts:
                        config['target'] = {**config['target'], **_hosts[_host_name]}
        else:
            sys.exit(
                output.message(
                    output.Subject.ERROR,
                    f'Local host file not found: {option["link_hosts"]}',
                    False
                )
            )



