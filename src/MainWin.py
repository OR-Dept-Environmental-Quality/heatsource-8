from __future__ import division
import wx, time, sys
import wxaddons.sized_controls as sc
import  wx.lib.filebrowsebutton as filebrowse
import  wx.lib.buttons  as  buttons
import  wx.gizmos   as  gizmos

from MainModel import MainModel
from Utils.Logger import Logger

class wxLogger(wx.TextCtrl):
    def __init__(self, parent, id):
        wx.TextCtrl.__init__(self, parent, id, size=(500,100), style=wx.TE_MULTILINE|wx.TE_AUTO_SCROLL|wx.TE_BESTWRAP|wx.TE_MULTILINE)
    def write(self, msg):
        if msg[-1] == '\n':
            self.WriteText(msg)
        else:
            self.AppendText(msg)


class HSFrame(sc.SizedFrame):
    def __init__(self, parent=None, id=-1):
        sc.SizedFrame.__init__(self, parent, id, "HeatSource Control Panel",
                               style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)

        self.wxTimer = wx.Timer(self)
        self.wxTimer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.OnWxTimer)
        self.StopWatch = wx.StopWatch()
        pane = self.GetContentsPane()
        pane.SetSizerType("Vertical")

        # row 0
        TopPane = sc.SizedPanel(pane, -1)
        TopPane.SetSizerType("horizontal")
        TopPane.SetSizerProps(expand=True)

        fbb = filebrowse.FileBrowseButton(TopPane, -1, \
                                               changeCallback = self.fbbCallback)
        fbb.SetSizerProps(expand=True, proportion=1)

        loadbtn = wx.Button(TopPane, -1, 'Load Model File')
        self.Bind(wx.EVT_BUTTON, self.OnLoadFile, loadbtn)

        # row 1
        # Set up a stdout/stderr logger
        self.ErrLog = Logger.getInstance()
        # Then create a wxTextCtrl to write to
        ErrLog = wxLogger(pane, -1)
        ErrLog.SetSizerProps(expand=True, proportion=1)
#        self.ErrLog.SetFile(ErrLog)  # Set the logger to the wxTextCtrl
        self.ErrLog.SetFile(sys.stdout) # Set the logger to the stdout

        # row 2
        MiddlePane = sc.SizedPanel(pane, -1)
        MiddlePane.SetSizerType("horizontal")

        self.Gauge = wx.Gauge(MiddlePane, -1, 1000, name="Remember: Patience is a Virtue!")
        self.Gauge.SetSizerProps(expand=True, proportion=1)
        self.Percent = wx.StaticText(MiddlePane, -1, "00%")
#        self.Percent.SetSizerProps(expand=True)
        font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.Percent.SetFont(font)

        MiddlePane.SetSizerProps(expand=True)

        # row 3
        # Main bottom panel
        BottomPane = sc.SizedPanel(pane, -1)
        BottomPane.SetSizerType("horizontal")
        BottomPane.SetSizerProps(expand=True)

        # Small panel for the runtime clock
        vpanel1 = sc.SizedPanel(BottomPane, -1)
        vpanel1.SetSizerType("vertical")

        # add a spacer
        spacer = sc.SizedPanel(BottomPane,-1)
        spacer.SetSizerProps(expand=True, proportion=1)

        # Small panel for the warnings number
        vpanel2 = sc.SizedPanel(BottomPane, -1)
        vpanel2.SetSizerType("vertical")
        vpanel2.SetSizerProps(expand=True,halign="center", proportion=0.5)

        # main font on small panel
        font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL)


        txt = wx.StaticText(vpanel1,-1,"Run Time:")
        self.LED = wx.StaticText(vpanel1, -1, "00:00")
        txt.SetFont(font)

        txt = wx.StaticText(vpanel2, -1, "Warnings:")
        self.NumWarnings = wx.StaticText(vpanel2, -1, "0")
        self.NumWarnings.SetFont(font)
        txt.SetFont(font)

        # add a spacer
        spacer = sc.SizedPanel(BottomPane,-1)
        spacer.SetSizerProps(expand=True, proportion=1)

        # Change the clock to a teletype font
        font = wx.Font(18, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD)

        # Add a button for starting, stopping the model
        self.LED.SetFont(font)
        self.StartStop = buttons.GenButton(BottomPane, -1, 'Big Red Button')
        self.Bind(wx.EVT_BUTTON, self.OnStartStop, self.StartStop)
        self.StartStop.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.StartStop.SetBezelWidth(5)
        self.StartStop.SetMinSize(wx.DefaultSize)
        self.StartStop.SetBackgroundColour("Grey")
        self.StartStop.SetForegroundColour(wx.WHITE)
        self.StartStop.SetToolTipString("Start or stop the model")
        self.StartStop.Enable(False)


        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.IsRunning = False
        self.LastLog = ""
        self.Log("HeatSource System started")
        self.FileName = None

        ################################
        ## debugging conveniences
#        self.FileName = "C:\\eclipse\\HeatSource\\Toketee_CCC.xls"
#        self.OnLoadFile(True)
#        self.OnStartStop(True)

    def Switch(self):
        """Routines necessary for switching the GUI on or off"""
        if not self.IsRunning: # Switching the model on
            self.StartStop.SetBackgroundColour("Red")
            self.StartStop.SetLabel("Big Red Button")
            self.StopWatch.Start(0)
            self.IsRunning = True
        else: # Switching off
            self.IsRunning = False
            self.StartStop.SetBackgroundColour("Green")
            self.StartStop.SetLabel("Start Model")
            self.StopWatch.Pause()
        return self.IsRunning

    def OnStartStop(self,evt):
        if self.Switch(): #Switch model on (GUI and timers)
            self.Model.Run()
            self.Switch()
            return
        else:
            self.Model.Stop()
            del self.Model
            self.Switch()
    def OnLoadFile(self,evt):
        if not self.FileName: return
        self.StartStop.Enable(True)
        self.Model = MainModel(self.FileName,self.Log)
        self.Model.Initialize()
        self.StartStop.SetBackgroundColour("Green")
        self.StartStop.SetLabel("Start Model")

    def fbbCallback(self,evt):
        self.FileName = evt.GetString()
        self.Log("Opened file, press 'Load Model File' to initialize model")

    def GetStopWatchTime(self):
        t = self.StopWatch.Time()
        s = t/1000
        m = int(s/60)
        s = int(s%60)
        h = int(m/60)
        if h > 1: m = int(m%60)
        return h,m,s
    def OnWxTimer(self,evt):
        if self.IsRunning:
            st = time.strftime("%M:%S", time.localtime(self.StopWatch.Time()/1000))
            self.LED.SetLabel(st)
            self.Gauge.Pulse()
    def Log(self,message,i=None, max=None):
        self.ErrLog.write(message)
        if i and max:
            self.Percent.SetLabel("%i%%"%int((i/max)*100))
            self.Gauge.Pulse()
class HSApp(wx.App):
    def OnInit(self):
        self.frame = HSFrame()
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = HSApp(False)
#    sys.stderr = Logger.getInstance()
    app.MainLoop()