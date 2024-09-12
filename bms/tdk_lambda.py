#!/usr/bin/python3
import serial, sys, argparse
from argparse import RawTextHelpFormatter
from time import sleep, time
from colorama import Fore, Style, Back

class Tdk():
    def __init__(self):
        self.s = self.con()
        self.adr6()

    def con(self):
        try:
            s = serial.Serial("/dev/ttyUSB0")
            s.baudrate=9600
            return s
        except Exception as e:
            print(f'{e}')
            sys.exit()

    def adr6(self):
            self.s.write(b'adr 6\r')
            sleep(0.2)
            o = self.s.read_all().decode('utf-8').strip()
    
    def dvc(self):
        """Voltage and Current data"""
        self.s.write(b'dvc?\r')
        sleep(0.2)
        o = self.s.read_all().decode('utf-8')
        o = o.split(',')
        print(f"Measured Voltage {Fore.GREEN}{Back.BLACK}{o[0]}{Style.RESET_ALL}\
              \nProgrammed Voltage {Fore.GREEN}{Back.BLACK}{o[1]}{Style.RESET_ALL}\
              \nMeasured Current {Fore.GREEN}{Back.BLACK}{o[2]}{Style.RESET_ALL}\
              \nProgrammed Current {Fore.GREEN}{Back.BLACK}{o[3]}{Style.RESET_ALL}\
              \nOver Voltage Set point {Fore.GREEN}{Back.BLACK}{o[4]}{Style.RESET_ALL}\
              \nUnder Voltage Set point {Fore.GREEN}{Back.BLACK}{o[5]}{Style.RESET_ALL}")
    
    def status(self):
        """Return the output ON/OFF status"""
        self.s.write(b'out?\r')
        sleep(0.2)
        o = self.s.read_all().decode('utf-8')
        print(o)

    def power_on(self):
        """Turns the output to ON"""
        self.s.write(b'out on\r')
        sleep(0.2)
        o = self.s.read_all().decode('utf-8')
        print('Power ON =>', o)
    
    def power_off(self):
        """Turns the output to OFF"""
        self.s.write(b'out off\r')
        sleep(0.2)
        o = self.s.read_all().decode('utf-8')
        print('Power OFF =>', o)
    
    def dvc_loop(self):
        while True:
            self.s.write(b'dvc?\r')
            sleep(0.2)
            o = self.s.read_all().decode('utf-8')
            o = o.split(',')
            voltage = o[0]
            current = o[2]
            print(f"\rMeasured Voltage {Fore.GREEN}{voltage}{Style.RESET_ALL}, Measured Current {Fore.GREEN}{current}{Style.RESET_ALL}, \
Timestamp {time()}", end='', flush=True)
            sleep(1)

    def close(self):
        self.s.close()

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.epilog = "COMMAND LIST:\n\
            status = Return the output ON/OFF status\n\
            power_on = Turns the output to ON\n\
            power_off = Turns the output to OFF\n\
            dvc = Voltage and Current data\n\
            dvc_loop = Voltage and Cutternt output in loop"
parser.add_argument("command", choices=['status', 'power_on', 'power_off', 'dvc', 'dvc_loop'], help="Command List")

args = parser.parse_args()
s = Tdk()

if args.command == 'status':
    s.status()
    s.close()
elif args.command == 'dvc':
    s.dvc()
    s.close()
elif args.command == 'dvc_loop':
    s.dvc_loop()
elif args.command == 'power_on':
    s.power_on()
    s.close()
elif args.command == 'power_off':
    s.power_off()
    s.close()