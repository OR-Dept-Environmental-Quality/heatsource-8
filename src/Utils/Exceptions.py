class HSError(Exception):
    """Base class for exceptions in this module."""
    pass

class HSClassError(HSError):
    """Exception raised for errors in class construction"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
