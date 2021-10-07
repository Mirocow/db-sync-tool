#!/usr/bin/env python3
# -*- coding: future_fstrings -*-

"""

"""
import requests
from db_sync_tool.utility import mode, system, output
from db_sync_tool import info


def print_header(mute):
    """
    Printing console header
    :param mute: Boolean
    :return:
    """
    # pylint: max-line-length=240
    if mute is False:
        print(output.CliFormat.BLACK + '##############################################' + output.CliFormat.ENDC)
        print(output.CliFormat.BLACK + '#                                            #' + output.CliFormat.ENDC)
        print(output.CliFormat.BLACK + '#' + output.CliFormat.ENDC + '                db sync tool                ' + output.CliFormat.BLACK + '#' + output.CliFormat.ENDC)
        print(output.CliFormat.BLACK + '#                   v' + info.__version__ + '                   #' + output.CliFormat.ENDC)
        print(output.CliFormat.BLACK + '#  ' + info.__homepage__ + '  #' + output.CliFormat.ENDC)
        print(output.CliFormat.BLACK + '#                                            #' + output.CliFormat.ENDC)
        print(output.CliFormat.BLACK + '##############################################' + output.CliFormat.ENDC)
        check_updates()


def check_updates():
    """

    :return:
    """
    response = requests.get(f'{info.__pypi_package_url__}/json')
    latest_version = response.json()['info']['version']
    comparable_latest_version = int(latest_version.replace('.', ''))
    comparable_actual_version = int(info.__version__.replace('.', ''))
    if comparable_actual_version < comparable_latest_version:
        output.message(
            output.Subject.WARNING,
            f'A new version {output.CliFormat.BOLD}v{latest_version}{output.CliFormat.ENDC} is available for the db-sync-tool: {info.__pypi_package_url__}',
            True
        )



def print_footer():
    """
    Printing console footer
    :return:
    """
    if system.config['dry_run']:
        _message = 'Successfully executed dry run'
    elif not system.config['keep_dump'] and \
            not system.config['is_same_client'] and \
            not mode.is_import():
        _message = 'Successfully synchronized databases'
    elif mode.is_import():
        _message = 'Successfully imported database dump'
    else:
        _message = 'Successfully created database dump'

    output.message(
        output.Subject.INFO,
        _message,
        True,
        True
    )