'''tzinfo timezone information for Indian/Cocos.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Cocos(StaticTzInfo):
    '''Indian/Cocos timezone definition. See datetime.tzinfo for details'''
    zone = 'Indian/Cocos'
    _utcoffset = timedelta(seconds=23400)
    _tzname = 'CCT'

Cocos = Cocos()

