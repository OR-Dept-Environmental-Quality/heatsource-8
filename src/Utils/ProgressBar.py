from __future__ import division
import wx


class ProgressBar(wx.ProgressDialog):
    """Simple progress dialog taking a message and a maximum count.

    Allows simplified access via call method as such:
    pb = ProgressBar("some text", max=100, parent=None)
    for i in xrange(100): pb()
    """
    def __init__(self, max, parent=None):
        wx.ProgressDialog.__init__(self,"HeatSource Progress Dialog",
                           "Patience is a virtue!",
                           maximum = max,
                           parent=parent,
                           style = wx.PD_CAN_ABORT
                            | wx.PD_AUTO_HIDE
                            | wx.PD_SMOOTH
                            #| wx.PD_APP_MODAL
                            #| wx.PD_ELAPSED_TIME
                            #| wx.PD_ESTIMATED_TIME
                            #| wx.PD_REMAINING_TIME
                            )
        self.gen = self.addOne(max)

    def __call__(self,msg=None,cur=0, max=100):
        msg = msg if msg else "Making progress"
        cur = cur if cur > 0 else 0.001
        msg += ": %i%%" % int((cur/max)*100)
        #return self.Update(self.gen.next())
        return self.Pulse(msg)

    def addOne(self, max):
        num = -1
        while num <= max:
            num += 1
            yield num
