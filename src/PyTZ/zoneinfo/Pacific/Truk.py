'''tzinfo timezone information for Pacific/Truk.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Truk(StaticTzInfo):
    '''Pacific/Truk timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Truk'
    _utcoffset = timedelta(seconds=36000)
    _tzname = 'TRUT'

Truk = Truk()

