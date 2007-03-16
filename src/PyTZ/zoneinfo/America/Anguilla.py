'''tzinfo timezone information for America/Anguilla.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Anguilla(DstTzInfo):
    '''America/Anguilla timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Anguilla'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1912,3,2,4,12,16),
        ]

    _transition_info = [
i(-15120,0,'LMT'),
i(-14400,0,'AST'),
        ]

Anguilla = Anguilla()

