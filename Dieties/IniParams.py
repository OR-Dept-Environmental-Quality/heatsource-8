from ConfigParser import SafeConfigParser,NoOptionError
from platform import platform
from os import environ, path, makedirs
from datetime import datetime, time
from time import strptime

class IniParamsDiety(dict):
    def __init__(self, *args):
        dict.__init__(self, *args)

IniParams = IniParamsDiety({'catchwidth':True})