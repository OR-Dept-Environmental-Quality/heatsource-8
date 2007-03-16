'''tzinfo timezone information for Pacific/Port_Moresby.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Port_Moresby(StaticTzInfo):
    '''Pacific/Port_Moresby timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Port_Moresby'
    _utcoffset = timedelta(seconds=36000)
    _tzname = 'PGT'

Port_Moresby = Port_Moresby()

