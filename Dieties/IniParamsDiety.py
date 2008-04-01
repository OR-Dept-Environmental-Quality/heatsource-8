""" The IniParams dictionary is simply a regular dictionary.
We just have it here because this is a good place to put
advanced options for the Heat Source module.

The idea here is that there are certain options
which we should include in the interface for daily
use, and certain options that we should hide in a place
where, to put it bluntly, people won't screw with them 
unless they're smart enough to know what they're doing.

Of course, you can't program against stupidity, but there you are.

Anyway, this is just a convenient place to hold them, where
they can be found at a later time. Of course, one important thing
to remember is that since many classes are built with the psyco
optimize switch, this module should be imported before any other
modules. Including the import in the Dieties.__init__.py module.

Good thing that very important caveat is buried deeply in these
notes where no-one will ever read it.
"""
from collections import defaultdict

class Interpolator(defaultdict):
    def __init__(self, *args, **kwargs):
        """Linearly interpolated dictionary class

        This class assumes a numeric key/value pair and will
        allow a linear interpolation between the
        all values, filling the dictionary with the results."""
        defaultdict.__init__(self)

IniParams = {"psyco": ('Dictionaries',
                        'BigRedButton',
                        'StreamNode',
                        'PyHeatsource',
                        'ExcelDocument',
                        'ExcelInterface',
                        'IniParamsDiety',
                        'ChronosDiety',
                        'Output'),
             "run_in_python": True,
             }