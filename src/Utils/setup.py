from distutils.core import setup, Extension
from distutils import msvccompiler

module1 = Extension('heatsource',
                    sources = ['heatsource.c'])

setup (name = 'HeatSource',
       version = '1.0',
       description = 'Various functions for the HeatSource system',
       ext_modules = [module1])
