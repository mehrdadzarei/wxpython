import os
import wx
import serial
import wx.html as html
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from time import sleep

class DataGen(object):
    # data = self.ser.read.GUI()
    def __init__(self):
        self.data = 0
        
    def next(self, data):
        while True:
             if len(data) == 0:
                  break
             # check if character is a delimeter
             if data == '\r':
                  data = '' # don't want returns. chuck it
            
             if data == '\n':
                  data = ''
             else:
                  return data
        # data = float(data)
        # self._recalc_data()
        # return self.data
    
    def _recalc_data(self):
        delta = np.random.uniform(-0.5, 0.5)
        r = np.random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8: 
            # attraction to the initial value
            delta += (0.5)# if self.data > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta

class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value

class GUI(wx.Frame):
   def __init__(self, parent):
      super(GUI, self).__init__(parent, size=(1000, 700))
      
      ########    scan ports     ##########
      for i in range(256):    # scan 256 ports
        try:
            self.ser = serial.Serial(i, timeout=0, writeTimeout=0)
            
            self.ser.close()   
        except serial.SerialException:
            pass
      #################
      self.ser.baudrate = 115200
      self.intensity = ['Level A', 'Level B', 'Level C', 'Level D', 'Level E']
      self.datagen = DataGen()
      self.data = []
      self.data1 = []
      self.save = False
      self.paused = True
      self.play = False
      
      self.creat_menubar()
      self.creat_toolbar()
      # self.statusbar = self.CreateStatusBar()
      # self.statusbar.SetStatusText("Pause")
      self.help()
      self.setting()
      self.plot()
      
      self.redraw_timer = wx.Timer(self)
      # self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
      # self.redraw_timer.Start(1)
      self.Bind(wx.EVT_PAINT, self.onpaint)
      self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)      
      self.SetTitle('NIRSOBL')
      self.Center()
      self.Show()
   
   def creat_menubar(self):
      menubar = wx.MenuBar()
      fileMenu = wx.Menu()
      fitem1 = wx.MenuItem(fileMenu, wx.ID_ANY, '&Open\tCtrl+O')
      fileMenu.AppendItem(fitem1)
      # fitem3 = wx.MenuItem(fileMenu, wx.ID_ANY, '&New\tCtrl+N')
      # fileMenu.AppendItem(fitem3)
      fitem4 = wx.MenuItem(fileMenu, wx.ID_ANY, '&Save\tCtrl+S')
      fileMenu.AppendItem(fitem4)
      fileMenu.AppendSeparator()
      fitem2 = wx.MenuItem(fileMenu, wx.ID_ANY, '&Quit\tCtrl+Q')
      fileMenu.AppendItem(fitem2)
      self.Bind(wx.EVT_MENU, self.OnQuit, id=fitem2.GetId())
      # self.Bind(wx.EVT_MENU, self.OnNew, id=fitem3.GetId())
      self.Bind(wx.EVT_MENU, self.OnSave, id=fitem4.GetId())
      self.Bind(wx.EVT_MENU, self.OnOpen, id=fitem1.GetId())
      menubar.Append(fileMenu, '&File')
      runMenu = wx.Menu()
      ritem1 = wx.MenuItem(runMenu, wx.ID_ANY, '&Run\tCtrl+R')
      runMenu.AppendItem(ritem1)
      self.Bind(wx.EVT_MENU, self.Run, id=ritem1.GetId())
      menubar.Append(runMenu, '&Run')
      setMenu = wx.Menu()
      sitem1 = wx.MenuItem(setMenu, wx.ID_ANY, '&Setting')
      setMenu.AppendItem(sitem1)
      self.Bind(wx.EVT_MENU, self.Set, id=sitem1.GetId())
      menubar.Append(setMenu, '&Setting')
      helpMenu = wx.Menu()
      help = wx.MenuItem(helpMenu, wx.ID_ANY, '&Help\tF1')
      helpMenu.AppendItem(help)
      self.Bind(wx.EVT_MENU, self.Help, id=help.GetId())
      menubar.Append(helpMenu, '&Help')
      self.SetMenuBar(menubar)
   
   def creat_toolbar(self):
      toolbar = self.CreateToolBar()
      topen = toolbar.AddLabelTool(wx.ID_ANY, 'Open', wx.Bitmap('icons/open.png'))
      toolbar.SetToolShortHelp(topen.GetId(),'Open (Ctrl+O)')
      # tnew = toolbar.AddLabelTool(wx.ID_ANY, 'New', wx.Bitmap('icons/new.png'))
      # toolbar.SetToolShortHelp(tnew.GetId(),'New (Ctrl+N)')
      tsave = toolbar.AddLabelTool(wx.ID_ANY, 'Save', wx.Bitmap('icons/save.png'))
      toolbar.SetToolShortHelp(tsave.GetId(),'Save (Ctrl+S)')
      trun = toolbar.AddLabelTool(wx.ID_ANY, 'Run', wx.Bitmap('icons/run.png'))
      toolbar.SetToolShortHelp(trun.GetId(),'Run (Ctrl+R)')
      tset = toolbar.AddLabelTool(wx.ID_ANY, 'Set', wx.Bitmap('icons/set1.png'))
      toolbar.SetToolShortHelp(tset.GetId(),'Setting')
      thelp = toolbar.AddLabelTool(wx.ID_ANY, 'Help', wx.Bitmap('icons/help.png'))
      toolbar.SetToolShortHelp(thelp.GetId(),'Help (F1)')
      toolbar.Realize()
      self.Bind(wx.EVT_TOOL, self.OnOpen, topen)
      # self.Bind(wx.EVT_TOOL, self.OnNew, tnew)
      self.Bind(wx.EVT_TOOL, self.OnSave, tsave)
      self.Bind(wx.EVT_TOOL, self.Run, trun)
      self.Bind(wx.EVT_TOOL, self.Set, tset)
      self.Bind(wx.EVT_TOOL, self.Help, thelp)
   
   def help(self):
      self.splitter = wx.SplitterWindow(self, -1)
      self.panelLeft = wx.Panel(self.splitter, -1)#, style=wx.BORDER_SUNKEN)
      self.panelRight = wx.Panel(self.splitter, -1)
      vbox2 = wx.BoxSizer(wx.VERTICAL)
      header = wx.Panel(self.panelRight, -1, size=(-1, 25))
      header.SetBackgroundColour('#6f6a59')
      header.SetForegroundColour('WHITE')
      hbox = wx.BoxSizer(wx.HORIZONTAL)
      st = wx.StaticText(header, -1, 'Help')#, (5, 1))
      font = st.GetFont()
      font.SetPointSize(9)
      st.SetFont(font)
      hbox.Add(st, 1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
      close = wx.BitmapButton(header, -1, wx.Bitmap('icons/close1.png'), 
		    style=wx.NO_BORDER)
      close.SetBackgroundColour('#6f6a59')
      hbox.Add(close, 0)
      header.SetSizer(hbox)
      vbox2.Add(header, 0, wx.EXPAND)
      help = html.HtmlWindow(self.panelRight, -1, style=wx.NO_BORDER)
      help.LoadPage('help.html')
      vbox2.Add(help, 1, wx.EXPAND)
      self.panelRight.SetSizer(vbox2)
      self.panelLeft.SetFocus()
      self.splitter.SplitVertically(self.panelLeft, self.panelRight)
      self.splitter.Unsplit()
      self.Bind(wx.EVT_BUTTON, self.CloseHelp, id=close.GetId())
   
   def setting(self):
      self.splitter1 = wx.SplitterWindow(self.panelLeft, -1)
      self.panelLefts = wx.Panel(self.splitter1, -1)#, style= wx.EXPAND)
      vboxls = wx.BoxSizer(wx.VERTICAL)
      headers = wx.Panel(self.panelLefts, -1, size=(-1, 30), style=wx.BORDER_SUNKEN)
      headers.SetBackgroundColour('#3B444B')
      headers.SetForegroundColour('WHITE')
      hboxls = wx.BoxSizer(wx.HORIZONTAL)
      stls = wx.StaticText(headers, -1, 'Setting', (5, 1))
      fonts = stls.GetFont()
      fonts.SetPointSize(9)
      stls.SetFont(fonts)
      hboxls.Add(stls, 1, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
      closes = wx.BitmapButton(headers, -1, wx.Bitmap('icons/close1.png'), 
		    style=wx.NO_BORDER)
      closes.SetBackgroundColour('#6f6a59')
      hboxls.Add(closes, 0)
      headers.SetSizer(hboxls)
      vboxls.Add(headers, 0, wx.EXPAND)
      texin = wx.StaticText(self.panelLefts, -1, 'Intensity: ', (45, 100))
      fontt = texin.GetFont()
      fontt.SetPointSize(9)
      texin.SetFont(fonts)
      self.inten = wx.ComboBox(self.panelLefts, pos=(100, 100), size=(100,30),
               choices=self.intensity, style=wx.CB_DROPDOWN)
      # vboxls.Add(self.inten, 0, wx.EXPAND)
      self.panelLefts.SetSizer(vboxls)
      self.Bind(wx.EVT_BUTTON, self.CloseSetting, id=closes.GetId())
   
   def plot(self):
      self.panelLeftp = wx.Panel(self.splitter1, -1)#, style=wx.BORDER_SUNKEN | wx.EXPAND)      
      # nb = wx.Notebooke(self.panelLeftp)
      # page1 = Plot(nb)
      self.vboxrp = wx.BoxSizer(wx.VERTICAL)
      headerp = wx.Panel(self.panelLeftp, -1, size=(-1, 30), style=wx.BORDER_SUNKEN)
      headerp.SetBackgroundColour('#3B444B')
      headerp.SetForegroundColour('WHITE')
      hboxrp = wx.BoxSizer(wx.HORIZONTAL)
      strp = wx.StaticText(headerp, -1, 'Plot', (5, 1))
      fontr = strp.GetFont()
      fontr.SetPointSize(9)
      strp.SetFont(fontr)
      hboxrp.Add(strp, 1, wx.TOP | wx.BOTTOM | wx.LEFT | wx.EXPAND, 5)
      headerp.SetSizer(hboxrp)
      ######### plot #######
      self.init_plot()
      self.canvas = FigCanvas(self.panelLeftp, -1, self.fig)

      self.xmin_control = BoundControlBox(self.panelLeftp, -1, "X min", 0)
      self.xmax_control = BoundControlBox(self.panelLeftp, -1, "X max", 100)
      self.ymin_control = BoundControlBox(self.panelLeftp, -1, "Y min", 0)
      self.ymax_control = BoundControlBox(self.panelLeftp, -1, "Y max", 100)
        
      self.pause_button = wx.Button(self.panelLeftp, -1, "Pause")
      self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
      # self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
      self.pause_button.SetLabel("Resume")
      self.stop_button = wx.Button(self.panelLeftp, -1, "Stop")
      self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.stop_button)
        
      self.cb_grid = wx.CheckBox(self.panelLeftp, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
      self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
      self.cb_grid.SetValue(True)
        
      self.cb_xlab = wx.CheckBox(self.panelLeftp, -1, 
            "Show X labels",
            style=wx.ALIGN_RIGHT)
      self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
      self.cb_xlab.SetValue(True)
        
      self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
      self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
      self.hbox1.AddSpacer(20)
      self.hbox1.Add(self.stop_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
      self.hbox1.AddSpacer(20)
      self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
      self.hbox1.AddSpacer(10)
      self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
      self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
      self.hbox2.AddSpacer(50)
      self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
      self.hbox2.AddSpacer(50)
      self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
      self.hbox2.AddSpacer(100)
      self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
      self.hbox2.AddSpacer(50)
      self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        
      # self.vbox = wx.BoxSizer(wx.VERTICAL)
      self.vboxrp.Add(headerp, 0, flag=wx.LEFT | wx.TOP | wx.EXPAND)      
      self.vboxrp.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
      self.vboxrp.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
      self.vboxrp.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
      self.panelLeftp.SetSizer(self.vboxrp)
      self.panelLeftp.SetFocus()
      self.splitter1.SplitVertically(self.panelLefts, self.panelLeftp,-1000)
      
   def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Chanel 1 data', size=10)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)
   
   def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.xmax_control.is_auto():
            xmax = len(self.data) if len(self.data) > 100 else 100
        else:
            xmax = int(self.xmax_control.manual_value())
            
        if self.xmin_control.is_auto():            
            xmin = xmax - 100
        else:
            xmin = int(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        if self.ymin_control.is_auto():
            ymin = round(min(self.data), 0) - 1
        else:
            ymin = int(self.ymin_control.manual_value())
        
        if self.ymax_control.is_auto():
            ymax = round(max(self.data), 0) + 1
        else:
            ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        pylab.setp(self.axes.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        # self.axes.set_xticks(np.arange(xmin,xmax+1,(xmax-xmin)/10))
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        # self.plot_data1.set_xdata(np.arange(len(self.data1)))
        # self.plot_data1.set_ydata(np.array(self.data1))
        
        self.canvas.draw()    
   
   def on_pause_button(self, event):
        self.paused = not self.paused
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
        if self.play:
            if not self.paused:
                # self.statusbar.SetStatusText("Ready")
                self.redraw_timer.Start(1)
                i = `self.inten.GetStringSelection()`
                self.ser.open()
                sleep(0.9)
                if i=="u''": self.ser.write("u'Level C'")
                else : self.ser.write(i)
            else:  
                # self.statusbar.SetStatusText("Pause")
                self.redraw_timer.Start(1000)
                sleep(0.9)
                self.ser.write("off")
                sleep(0.9)         # if don't put this code the program will out
                self.ser.close()
    
   # def on_update_pause_button(self, event):
        # label = "Resume" if self.paused else "Pause"
        # self.pause_button.SetLabel(label)
    
   def on_cb_grid(self, event):
        self.draw_plot()
    
   def on_cb_xlab(self, event):
        self.draw_plot()
       
   def OnQuit(self, e):
      self.Close()
      
   def Run(self, e):
      self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
      self.redraw_timer.Start(1)
      # self.statusbar.SetStatusText("Ready")
      self.paused = False
      self.pause_button.SetLabel("Pause")
      self.play = True
      i = `self.inten.GetStringSelection()`
      self.ser.close()
      self.ser.open()
      sleep(0.9)    # this is for respons of arduino
      if i=="u''": self.ser.write("u'Level C'")
      else : self.ser.write(i)
      # plot the data as a line series, and save the reference 
      # to the plotted line series
      #
      self.plot_data = self.axes.plot(
            self.data, 
            linewidth=1,
            color=(1, 1, 0),
            )[0]
      # self.plot_data1 = self.axes.plot(
            # self.data1, 
            # linewidth=1,
            # color=(1, 0, 0),
            # )[0]
      
   def on_stop_button(self, e):
      if self.play:
           self.play = False
           if self.ser.isOpen():
                self.redraw_timer.Start(1000)
                sleep(0.9)
                self.ser.write("off")
                sleep(0.9)         # if don't put this code the program will out
                self.ser.close()
           if self.save == True:
                self.save = False
                self.f.close()
      
   def OnOpen(self, e):
      print 'presed open'
      
   def OnSave(self, e):
      self.file_choices = "Text Documents (*.txt)|*.txt"
        
      self.dlg = wx.FileDialog(
            self, 
            message="Save data as...",
            defaultDir=os.getcwd(),
            defaultFile="fnirs.txt",
            wildcard=self.file_choices,
            style=wx.SAVE)
        
      if self.dlg.ShowModal() == wx.ID_OK:
          path = self.dlg.GetPath()
          self.f = open(path, 'w')
          self.save = True

   def Help(self, e):
      x,y = self.GetSize()
      self.splitter.SplitVertically(self.panelLeft, self.panelRight, x-300)
      self.panelLeft.SetFocus()
      self.splitter1.SetSize((x-300,y-90))

   def CloseHelp(self, e):
      x,y = self.GetSize()
      self.splitter1.SetSize((x,y-90))
      self.splitter.Unsplit()
      self.panelLeft.SetFocus()
  
   def Set(self, e):
      x,y = self.panelLeft.GetSize()
      self.splitter1.Unsplit()
      self.splitter1.SplitVertically(self.panelLefts, self.panelLeftp, -x+300)
      self.panelLeftp.SetFocus()

   def CloseSetting(self, e):
      x,y = self.GetSize()
      self.splitter1.Unsplit()
      self.splitter1.SplitVertically(self.panelLefts, self.panelLeftp, -x)
      self.panelLeft.SetFocus()
  
   def onpaint(self, e):
      x,y = self.GetSize()
      self.splitter.SetSize((x-20,y))
      self.splitter1.SetSize((x,y-90))
      self.splitter.Unsplit()
   
   def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        # print 'x'
        if self.ser.isOpen():
             # data = self.ser.readline()
             # x = self.datagen.next(data)
             # print x
             if not self.paused:
                  while True:
                       c = self.ser.readline() # attempt to read a character from Serial
                       #was anything read?
                       if len(c) == 0:
                            break
                       # check if character is a delimeter
                       if c == '\r':
                            c = '' # don't want returns. chuck it
                       if c == '\n':
                            c = ''
                       else:
                           self.data.append(float(c))
                           # print self.data
                           if self.save == True:
                               self.f.write(`float(c)`)
                               self.f.write('\n')
             self.draw_plot()
     
   def OnCloseWindow(self, e):
           dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Exit',
              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
           ret = dial.ShowModal()
           if ret==wx.ID_YES:
                self.Destroy()
           else:
                e.Veto()

def main():
   app = wx.App()
   GUI(None)
   app.MainLoop()

if __name__=='__main__':
    main()