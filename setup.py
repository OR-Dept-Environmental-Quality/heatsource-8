#!/usr/bin/env python2

from distutils.core import setup, Extension
from sys import version_info as VI

DISTUTILS_DEBUG = True

if VI < (2,5):
    v = "%i.%i" %(VI[0],VI[1])
    raise Exception("Default Python version must be >2.5, not %s" % v)

setup(name='heatsource808',
      version='8.0.8.1',
      classifiers=[
          'Development Status :: 6 - Mature',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python :: 2.5',
          'Topic :: Scientific/Engineering'
      ],
      long_description="""Heat Source is a computer model
      used by the Oregon Department of Environmental Quality
      to simulate stream thermodynamics and hydraulic routing.
      It was originally developed by Matt Boyd in 1996 as a
      Masters Thesis at Oregon State Universityin the Departments
      of Bioresource Engineering and Civil Engineering. Since
      then it has grown and changed significantly. Oregon DEQ
      currently maintains the Heat Source methodology and computer
      programming. Appropriate model use and application are the
      sole responsibility of the user.""",
      description='One-dimensional stream temperature modeling program',
      url='https://www.oregon.gov/deq/wq/tmdls/Pages/TMDLs-Tools.aspx',
      author='Matt Boyd, Brian Kasper, John Metta, Ryan Michie, Dan Turner',
      maintainer='Ryan Michie, Oregon DEQ',
      maintainer_email='ryan.michie@deq.oregon.gov',
      platforms=['win32'],
      license=['GNU General Public License v3 (GPLv3)'],
      packages=['heatsource808',
                'heatsource808.Dieties',
                'heatsource808.Excel',
                'heatsource808.Stream',
                'heatsource808.Utils'],
      data_files=[('Lib/site-packages/heatsource808',['src/heatsource808/HSmodule.pyd'])],
      #ext_modules=[Extension('heatsource808.HSmodule',['src/heatsource808/HSmodule.c'])],
      package_dir={'': 'src'},
      requires=['win32com','win32gui'],
      )
