#!/usr/bin/env python

from typing import List
from gpiozero import Button
import requests
from time import sleep


BUTTON_GPIO = 14
DEVICES = ['207', '208']   # IP addresses of smart sockets on local network


def execute_command(device: str, command: str) -> bool:
    url = f'http://192.168.1.{device}/relay/0?turn={command}'

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


def control_lights(devices: List[str], command: str) -> None:
    successes = [False for device in devices]

    while not all(successes):
        for index, device in enumerate(devices):
            if not successes[index]:
                success = execute_command(device, command)
                successes[index] = success
        
        if not all(successes):
            sleep(5)


def startup():
    button = Button(BUTTON_GPIO)

    if button.is_held:
        # Inverse logic
        control_lights(DEVICES, 'off')
    else:
        control_lights(DEVICES, 'on')


if __name__ == '__main__':
    button = Button(BUTTON_GPIO)

    while True:
        # Inverse logic
        button.wait_for_press()
        control_lights(DEVICES, 'off')
        button.wait_for_release()
        control_lights(DEVICES, 'on')