import matplotlib
matplotlib.use('WX')
from matplotlib.backends.backend_wx import FigureCanvasWx,\
     FigureManager, NavigationToolbar2Wx

from matplotlib.figure import Figure
from matplotlib.axes import Subplot
import matplotlib.numerix as numpy
import wx


TIMER_ID = wx.NewId()

class DynaPlot(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Test embedded wxFigure")

        self.fig = Figure((5,4), 75)
        self.canvas = FigureCanvasWx(self, -1, self.fig)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))

        # Create a figure manager to manage things
        self.figmgr = FigureManager(self.canvas, 1, self)
        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        wx.EVT_TIMER(self, TIMER_ID, self.onTimer)

    def Initialize(self, X,Y):
        self.X = X
        self.Y = Y
        a = self.fig.add_subplot(111)
        self.ind = numpy.arange(60)
        self.lines = a.plot(X,Y,'-')

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onTimer(self, evt):
        self.lines[0].set_data(self.X, self.Y)
        self.canvas.draw()
        self.canvas.gui_repaint()
