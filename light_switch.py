#!/usr/bin/env python

import json
import configparser
import json
from dataclasses import dataclass
from typing import List
from gpiozero import Button
import requests
from time import sleep


CONFIG_FILENAME = 'config.ini'


def execute_command(socket: str, command: str) -> bool:
    url = f'http://{socket}/relay/0?turn={command}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f'Successfully executed {url}.')
            return True
        else:
            print(f'Failed to execute {url}. Response: {response.status_code}')
            return False
    except requests.RequestException as e:
        print(f'Error occurred: {e}')
        return False


def control_lights(sockets: List[str], command: str) -> None:
    successes = [False for _ in sockets]

    while not all(successes):
        for index, socket in enumerate(sockets):
            if not successes[index]:
                success = execute_command(socket, command)
                successes[index] = success
        
        if not all(successes):
            sleep(2)


def startup(button, config):
    if button.is_held:
        # Inverse logic
        control_lights(config.sockets, 'off')
    else:
        control_lights(config.sockets, 'on')


@dataclass
class Configuration:
    sockets: List[str]
    button_gpio: int


def get_config(filename: str):
    config_parser = configparser.ConfigParser()
    config_parser.read(filename)
    sockets = json.loads(config_parser.get('config', 'sockets'))
    button_gpio = int(config_parser['config']['button_gpio'])
    config = Configuration(sockets, button_gpio)
    return config
    

if __name__ == '__main__':
    config = get_config(CONFIG_FILENAME)
    button = Button(config.button_gpio)
    startup(button, config)

    while True:
        # Inverse logic
        button.wait_for_press()
        control_lights(config.sockets, 'off')
        button.wait_for_release()
        control_lights(config.sockets, 'on')