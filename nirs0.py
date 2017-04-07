import os                                      #for open and save files
import wx                                      #for create GUI
import wx.lib.buttons                          #for buttons image
import wx.aui                                  #for notebook that have close icon
import serial                                   
import wx.html as html
import matplotlib
matplotlib.use('WXAgg')                        #for pin plot in window
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from time import sleep,time
import threading

class Process(wx.Panel):
     def __init__(self,parent):
         wx.Panel.__init__(self, parent)
        
         self.run = wx.Button(self, -1, "Run", pos = (50,50))
         self.Bind(wx.EVT_BUTTON, self.Run, self.run)
         
     def Run(self,e):
         print "started"

class Analyze(wx.Panel):
     def __init__(self,parent):
         wx.Panel.__init__(self, parent)
         self.figure = Figure()
         self.canv = FigCanvas(self,-1, self.figure)
         self.toolbar = NavigationToolbar(self.canv)
         self.toolbar.Hide()
         
         self.home = wx.lib.buttons.GenBitmapButton(self, -1, wx.Bitmap('icons/home.jpg'))
         self.Bind(wx.EVT_BUTTON, self.Home, self.home)
         
         self.pan = wx.lib.buttons.GenBitmapButton(self, -1, wx.Bitmap('icons/pan.png'))
         self.Bind(wx.EVT_BUTTON, self.Pan, self.pan)
         
         self.zoom = wx.lib.buttons.GenBitmapButton(self, -1, wx.Bitmap('icons/zoom.jpg'))
         self.Bind(wx.EVT_BUTTON, self.Zoom, self.zoom)
         
         self.plot = wx.lib.buttons.GenBitmapButton(self, -1, wx.Bitmap('icons/plot.png'))
         self.Bind(wx.EVT_BUTTON, self.Plot_a, self.plot)
         
         self.process = wx.lib.buttons.GenBitmapButton(self, -1, wx.Bitmap('icons/processing.png'))
         self.Bind(wx.EVT_BUTTON, self.Processing, self.process)
         
         self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
         self.hbox1.Add(self.home, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
         self.hbox1.Add(self.pan, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
         self.hbox1.Add(self.zoom, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
         self.hbox1.Add(self.plot, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
         self.hbox1.Add(self.process, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
         
         self.vbox = wx.BoxSizer(wx.VERTICAL)
         self.vbox.Add(self.canv, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
         self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_CENTER | wx.TOP)
         self.SetSizer(self.vbox)
         
     def Home(self,e):
         self.toolbar.home()
         
     def Pan(self,e):
         self.toolbar.pan()
     
     def Zoom(self,e):
         self.toolbar.zoom()
     
     def Plot_a(self,e):
         data = [np.random.random() for i in range(25)]
         
         ax = self.figure.add_subplot(111)
         ax.hold(False)
         ax.plot(data, '*-')
         self.canv.draw()
     
     def Processing(self,e):
         print "run process"
         
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
         
         self.intensity = ['Level A', 'Level B', 'Level C', 'Level D', 'Level E']
         self.save = False
         self.paused = True
         self.play = False
         self.cnt = 0                    #number of press Run
      
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
   
     def serial(self):
         for i in range(256):    # scan 256 ports
             try:
                 # print "asdf"
                 #1 in blow statment is for don't execut port 0, becuase this port is open
                 self.ser = serial.Serial(i+1,baudrate=250000,
                                              bytesize=serial.EIGHTBITS,
                                              parity=serial.PARITY_NONE,
                                              stopbits=serial.STOPBITS_ONE,
                                              timeout=0,
                                              xonxoff=0,
                                              rtscts=0,
                                              interCharTimeout=None)
             except serial.SerialException:
                 pass
             
     def creat_menubar(self):
         menubar = wx.MenuBar()
         fileMenu = wx.Menu()
         runMenu = wx.Menu()
         setMenu = wx.Menu()
         #############  File Menu  ################
         fitem1 = wx.MenuItem(fileMenu, wx.ID_ANY, '&Open\tCtrl+O')
         # fitem3 = wx.MenuItem(fileMenu, wx.ID_ANY, '&New\tCtrl+N')
         fitem4 = wx.MenuItem(fileMenu, wx.ID_ANY, '&Save\tCtrl+S')
         fitem2 = wx.MenuItem(fileMenu, wx.ID_ANY, '&Quit\tCtrl+Q')
         
         self.Bind(wx.EVT_MENU, self.OnQuit, id=fitem2.GetId())
         # self.Bind(wx.EVT_MENU, self.OnNew, id=fitem3.GetId())
         self.Bind(wx.EVT_MENU, self.OnSave, id=fitem4.GetId())
         self.Bind(wx.EVT_MENU, self.OnOpen, id=fitem1.GetId())
         
         fileMenu.AppendItem(fitem1)
         # fileMenu.AppendItem(fitem3)
         fileMenu.AppendItem(fitem4)
         fileMenu.AppendSeparator()
         fileMenu.AppendItem(fitem2)
         menubar.Append(fileMenu, '&File')
         ##################
         #############  run Menu  ################
         ritem1 = wx.MenuItem(runMenu, wx.ID_ANY, '&Run\tCtrl+R')
         runMenu.AppendItem(ritem1)
         self.Bind(wx.EVT_MENU, self.Run, id=ritem1.GetId())
         menubar.Append(runMenu, '&Run')
         ##################
         #############  setting Menu  ################
         sitem1 = wx.MenuItem(setMenu, wx.ID_ANY, '&Setting')
         setMenu.AppendItem(sitem1)
         self.Bind(wx.EVT_MENU, self.Set, id=sitem1.GetId())
         menubar.Append(setMenu, '&Setting')
         ##################
         #############  Help Menu  ################
         helpMenu = wx.Menu()
         help = wx.MenuItem(helpMenu, wx.ID_ANY, '&Help\tF1')
         helpMenu.AppendItem(help)
         self.Bind(wx.EVT_MENU, self.Help, id=help.GetId())
         menubar.Append(helpMenu, '&Help')
         ##################
         self.SetMenuBar(menubar)
    
     def creat_toolbar(self):
         toolbar = self.CreateToolBar()
         toolbar.SetBackgroundColour('#0048BA')
         
         topen = toolbar.AddLabelTool(wx.ID_ANY, 'Open', wx.Bitmap('icons/open.png'))
         toolbar.SetToolShortHelp(topen.GetId(),'Open (Ctrl+O)')
         
         tsave = toolbar.AddLabelTool(wx.ID_ANY, 'Save', wx.Bitmap('icons/save.png'))
         toolbar.SetToolShortHelp(tsave.GetId(),'Save (Ctrl+S)')
         
         trun = toolbar.AddLabelTool(wx.ID_ANY, 'Run', wx.Bitmap('icons/run.png'))
         toolbar.SetToolShortHelp(trun.GetId(),'Run (Ctrl+R)')
         
         tset = toolbar.AddLabelTool(wx.ID_ANY, 'Set', wx.Bitmap('icons/set1.png'))
         toolbar.SetToolShortHelp(tset.GetId(),'Setting')
         
         toolbar.AddSeparator()
         
         thelp = toolbar.AddLabelTool(wx.ID_ANY, 'Help', wx.Bitmap('icons/help.png'))
         toolbar.SetToolShortHelp(thelp.GetId(),'Help (F1)')
         
         toolbar.Realize()
         self.Bind(wx.EVT_TOOL, self.OnOpen, topen)
         self.Bind(wx.EVT_TOOL, self.OnSave, tsave)
         self.Bind(wx.EVT_TOOL, self.Run, trun)
         self.Bind(wx.EVT_TOOL, self.Set, tset)
         self.Bind(wx.EVT_TOOL, self.Help, thelp)
   
     def help(self):
         self.splitter = wx.SplitterWindow(self, -1)
         self.panelLeft = wx.Panel(self.splitter, -1)#, style=wx.BORDER_SUNKEN)
         self.panelRight = wx.Panel(self.splitter, -1)
         
         header = wx.Panel(self.panelRight, -1, size=(-1, 25))
         header.SetBackgroundColour('#6f6a59')
         header.SetForegroundColour('WHITE')
         st = wx.StaticText(header, -1, 'Help')#, (5, 1))
         font = st.GetFont()
         font.SetPointSize(9)
         st.SetFont(font)
         close = wx.BitmapButton(header, -1, wx.Bitmap('icons/close1.png'), 
		     style=wx.NO_BORDER)
         
         hbox = wx.BoxSizer(wx.HORIZONTAL)
         hbox.Add(st, 1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
         hbox.Add(close, 0)
         header.SetSizer(hbox)
         
         help = html.HtmlWindow(self.panelRight, -1, style=wx.NO_BORDER)
         help.LoadPage('help.html')
         
         vbox2 = wx.BoxSizer(wx.VERTICAL)
         vbox2.Add(header, 0, wx.EXPAND)
         vbox2.Add(help, 1, wx.EXPAND)
         self.panelRight.SetSizer(vbox2)
         self.panelLeft.SetFocus()
         self.splitter.SplitVertically(self.panelLeft, self.panelRight)
         self.splitter.Unsplit()
         
         self.Bind(wx.EVT_BUTTON, self.CloseHelp, id=close.GetId())
   
     def setting(self):
         self.splitter1 = wx.SplitterWindow(self.panelLeft, -1)
         self.panelLefts = wx.Panel(self.splitter1, -1)#, style= wx.EXPAND)
         
         headers = wx.Panel(self.panelLefts, -1, size=(-1, 30), style=wx.BORDER_SUNKEN)
         headers.SetBackgroundColour('#3B444B')
         headers.SetForegroundColour('WHITE')
         
         stls = wx.StaticText(headers, -1, 'Setting', (5, 1))
         fonts = stls.GetFont()
         fonts.SetPointSize(9)
         stls.SetFont(fonts)

         closes = wx.BitmapButton(headers, -1, wx.Bitmap('icons/close1.png'), 
		     style=wx.NO_BORDER)
         closes.SetBackgroundColour('#6f6a59')
         
         hboxls = wx.BoxSizer(wx.HORIZONTAL)
         hboxls.Add(stls, 1, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
         hboxls.Add(closes, 0)
         headers.SetSizer(hboxls)
         vboxls = wx.BoxSizer(wx.VERTICAL)
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
         self.nb = wx.aui.AuiNotebook(self.panelLeftp)
         # self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.close_nb, self.nb)
         
         sizer = wx.BoxSizer(wx.VERTICAL)
         sizer.Add(self.nb, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
         self.panelLeftp.SetSizer(sizer)
         self.splitter1.SplitVertically(self.panelLefts, self.panelLeftp,-1000)
     
     def page1(self):
         self.pag = wx.Panel(self.nb, id = self.cnt)
         self.data = []
         self.data1 = []
         self.t = 0
         self.init_plot()
         self.canvas = FigCanvas(self.pag, -1, self.fig)
         
         self.xmin_control = BoundControlBox(self.pag, -1, "X min", 0)
         self.xmax_control = BoundControlBox(self.pag, -1, "X max", 100)
         self.ymin_control = BoundControlBox(self.pag, -1, "Y min", 0)
         self.ymax_control = BoundControlBox(self.pag, -1, "Y max", 100)
        
         self.pause_button = wx.Button(self.pag, -1, "Pause")
         self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
         # self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
         self.pause_button.SetLabel("Resume")
         self.stop_button = wx.Button(self.pag, -1, "Stop")
         self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.stop_button)
         
         self.cb_grid = wx.CheckBox(self.pag, -1, 
             "Show Grid",
             style=wx.ALIGN_RIGHT)
         self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
         self.cb_grid.SetValue(True)
        
         self.cb_xlab = wx.CheckBox(self.pag, -1, 
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
         
         self.vboxrp = wx.BoxSizer(wx.VERTICAL)
         self.vboxrp.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
         self.vboxrp.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
         self.vboxrp.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
         self.pag.SetSizer(self.vboxrp)
         # self.panelLeftp.SetFocus()
         self.nb.AddPage(self.pag,"Plot %d" %self.cnt, select = True)
         vboxp = wx.BoxSizer(wx.VERTICAL)
         vboxp.Add(self.nb, 1, wx.EXPAND)
         self.SetSizer(vboxp)
         
     def init_plot(self):
         self.dpi = 100
         self.fig = Figure((3.0, 3.0), dpi=self.dpi)
         
         self.axes = self.fig.add_subplot(111)
         self.axes.set_axis_bgcolor('black')
         self.axes.set_title('Chanel 1 data', size=10)
         self.axes.set_xlabel('time (ms)', size = 10)
         self.axes.set_ylabel('Amplitude ()', size = 10)
         
         # self.axes1 = self.fig.add_subplot(212)
         # self.axes1.set_axis_bgcolor('black')
         # self.axes1.set_title('Chanel 2 data', size=10)
         # self.axes1.set_xlabel('time (ms)', size = 10)
         # self.axes1.set_ylabel('Amplitude ()', size = 10)
        
         pylab.setp(self.axes.get_xticklabels(), fontsize=8)
         pylab.setp(self.axes.get_yticklabels(), fontsize=8)
         
         # pylab.setp(self.axes1.get_xticklabels(), fontsize=8)
         # pylab.setp(self.axes1.get_yticklabels(), fontsize=8)
   
     def draw_plot(self):
         while True:
             try:
                 if self.xmax_control.is_auto():
                     xmax = len(self.data) if len(self.data) > 100 else 100
                 else:
                     xmax = int(self.xmax_control.manual_value())
            
                 if self.xmin_control.is_auto():            
                     xmin = xmax - 100
                 else:
                     xmin = int(self.xmin_control.manual_value())

                 if self.ymin_control.is_auto():
                     ymin = round(min(min(self.data),min(self.data1)), 0) - 1
                 else:
                     ymin = int(self.ymin_control.manual_value())
        
                 if self.ymax_control.is_auto():
                     ymax = round(max(max(self.data),max(self.data1)), 0) + 1
                 else:
                     ymax = int(self.ymax_control.manual_value())

                 self.axes.set_xbound(lower=xmin, upper=xmax)
                 self.axes.set_ybound(lower=ymin, upper=ymax)
                 
                 # self.axes1.set_xbound(lower=xmin, upper=xmax)
                 # self.axes1.set_ybound(lower=ymin, upper=ymax)
        
                 if self.cb_grid.IsChecked():
                     self.axes.grid(True, color='gray')
                     # self.axes1.grid(True, color='gray')
                 else:
                     self.axes.grid(False)
                     # self.axes1.grid(False)

                 pylab.setp(self.axes.get_xticklabels(), 
                            visible=self.cb_xlab.IsChecked())
                            
                 # pylab.setp(self.axes1.get_xticklabels(), 
                            # visible=self.cb_xlab.IsChecked())
                 # print np.arange(float(len(self.data))/4000)
                 #4.0 is for sampling rate in ADC that its rate is 4 kHz
                 self.plot_data.set_xdata(np.arange(len(self.data)))
                 self.plot_data.set_ydata(np.array(self.data))
                 self.plot_data1.set_xdata(np.arange(len(self.data1)))
                 self.plot_data1.set_ydata(np.array(self.data1))
         
                 self.canvas.draw()
                 break
             except:
                 break    
   
     def on_pause_button(self, event):
         self.paused = not self.paused
         label = "Resume" if self.paused else "Pause"
         self.pause_button.SetLabel(label)
         if self.play:
             if not self.paused:
                 # self.statusbar.SetStatusText("Ready")
                 self.redraw_timer.Start(1)
                 i = `self.inten.GetStringSelection()`
                 while True:
                     try:
                         self.ser.open()
                         sleep(0.9)
                         if i=="u''": self.ser.write("'Level C'")
                         else : self.ser.write(i[1:])
                         break
                     except:
                         dial = wx.MessageDialog(None, 'Port Not Connected\
                             \nYou Should Connected System Or \
                             \nReconnected It', 'Error',
                             wx.OK | wx.ICON_ERROR)
                         ret = dial.ShowModal()
                         self.play = False
                         break
             else:  
                 # self.statusbar.SetStatusText("Pause")
                 while True:
                     try:
                         self.redraw_timer.Start(5000)
                         sleep(0.9)
                         self.ser.write("off")
                         sleep(0.9)         # if don't put this code the program will out
                         self.ser.close()
                         break
                     except:
                         dial = wx.MessageDialog(None, 'Port Not Connected\
                             \nYou Should Connected System Or \
                             \nReconnected It', 'Error',
                             wx.OK | wx.ICON_ERROR)
                         ret = dial.ShowModal()
                         self.play = False
                         break
    
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
         if not self.play:
             self.serial()
             while True:
                 try:
                     if not self.ser.isOpen(): self.ser.open()
                     elif self.ser.isOpen():
                         self.cnt += 1
                         self.page = self.page1()
                         
                         self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
                         self.redraw_timer.Start(1)
                         # self.statusbar.SetStatusText("Ready")
                         self.paused = False
                         self.pause_button.SetLabel("Pause")
                         self.play = True
                         i = `self.inten.GetStringSelection()`
                         # print i[1:], type(i)
                         self.ser.close()
                         self.ser.open()
                         sleep(0.9)    # this is for respons of arduino
                         if i=="u''": self.ser.write("'Level C'")
                         else : self.ser.write(i[1:])
                         self.p = threading.Thread(target=self.received_data)
                         self.r = 1
                         self.p.start()
                         # plot the data as a line series, and save the reference 
                         # to the plotted line series
                         #
                         self.plot_data = self.axes.plot(
                             self.data, 
                             linewidth=1,
                             color='red',#(1, 1, 0),
                             label = "730 nm",
                             )[0]
                         self.plot_data1 = self.axes.plot(
                             self.data1, 
                             linewidth=1,
                             color='blue',#(1, 0, 0),
                             label = "850 nm",
                             )[0]
                         self.axes.legend(handles=[self.plot_data,self.plot_data1])
                         # self.axes1.legend(handles=[self.plot_data,self.plot_data1])
                     break
                 except:
                     dial = wx.MessageDialog(None, 'Port Not Connected\
                             \nYou Should Connected System Or \
                             \nReconnected It', 'Error',
                             wx.OK | wx.ICON_ERROR)
                     ret = dial.ShowModal()
                     break
      
     def on_stop_button(self, e):
         if self.play:
             self.play = False
             if self.ser.isOpen():
                 self.redraw_timer.Start(5000)
                 self.r = 0
                 sleep(1)
                 self.ser.write("off")
                 sleep(0.9)         # if don't put this code the program will out
                 self.ser.close()
             if self.save == True:
                 self.save = False
                 self.f.close()
      
     def OnOpen(self, e):
         file_choices = "Text Documents (*.txt)|*.txt"
        
         dlg = wx.FileDialog(
             self, 
             message="Chose a data file...",
             defaultDir=os.getcwd(),
             defaultFile="",
             wildcard=file_choices,
             style=wx.FD_OPEN)
        
         if dlg.ShowModal() == wx.ID_OK:
             path = dlg.GetPath()
            
             self.filename = os.path.split(os.path.splitext(path)[0])[1]
             self.analyze = Analyze(self.nb)#self.analyse()
             self.nb.AddPage(self.analyze, self.filename, select=True)
             vboxa = wx.BoxSizer(wx.VERTICAL)
             vboxa.Add(self.nb, 1, wx.EXPAND)
             self.SetSizer(vboxa)
         
     def OnSave(self, e):
         file_choices = "Text Documents (*.txt)|*.txt"
        
         dlg = wx.FileDialog(
             self, 
             message="Save data as...",
             defaultDir=os.getcwd(),
             defaultFile="fnirs.txt",
             wildcard=file_choices,
             style=wx.SAVE)
        
         if dlg.ShowModal() == wx.ID_OK:
             path = dlg.GetPath()
             self.f = open(path, 'w')
             self.f.write('time (ms)')
             self.f.write('\t')
             self.f.write('730 nm') 
             self.f.write('\t')
             self.f.write('850 nm') 
             self.f.write('\n')
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
       # while self.t:  
         while True:
             try :
                 #when last notebook of plot is closed the if clause is error
                 if self.pag.GetId() == self.cnt:
                     break
             except:
                 if self.ser.isOpen():
                         self.play = False
                         self.redraw_timer.Start(5000)
                         sleep(0.9)
                         self.ser.write("off")
                         sleep(0.9)         # if don't put this code the program will out
                         self.ser.close()
                 break
         if self.ser.isOpen():
             # data = self.ser.readline()
             if not self.paused:
                 self.draw_plot()
                             # if self.save == True:
                                 # while True:
                                     # try:
                                         # self.f.write(`len(self.data)/4.0`)
                                         # self.f.write('\t\t')
                                         # self.f.write(`d`) 
                                         # self.f.write('\t\t')
                                         # self.f.write(`0`) 
                                         # self.f.write('\n')
                                         # break
                                     # except:
                                         # break
                         
                             # if self.save == True:
                                 # while True:
                                     # try:
                                         # self.f.write(`len(self.data)/4.0`)
                                         # self.f.write('\t\t')
                                         # self.f.write(`0`) 
                                         # self.f.write('\t\t')
                                         # self.f.write(`d`) 
                                         # self.f.write('\n')
                                         # break
                                     # except:
                                         # break
                         
                 
     
     def received_data(self):
         while self.r:
             if self.ser.isOpen():
                 # data = self.ser.readline()
                 if not self.paused:
                     #return a float value or try a few times until we get one
                     self.ser.write("'Level A'")
                     for i in range(39):
                         if len(self.data)==100: del self.data[0]; del self.data1[0]
                         self.data.append(self.channel())
                         self.data1.append(0)
                     self.ser.write("'Level B'")
                     for i in range(39):
                         if len(self.data)==100: del self.data[0]; del self.data1[0]
                         self.data.append(0)
                         self.data1.append(self.channel())
                         
     def channel(self):
         for i in range(50):
             buffer = ''
             while True:
                 try:  
                     buffer = buffer + self.ser.readline()
                     if '\n' in buffer:
                         received = buffer
                         #If the Arduino sends lots of empty lines, you'll lose the
                         #last filled line, so you could make the above statement conditional
                         #like so: if lines[-2]: last_received = lines[-2]
                         buffer = ''
                         break
                 except: pass
             try:
                 # strip Return a copy of the string with the leading and trailing characters removed
                 return float(received.strip())
             except ValueError:
                 pass
     
     def OnCloseWindow(self, e):
             dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Exit',
                 wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
             ret = dial.ShowModal()
             if ret==wx.ID_YES:
                 while True:
                     try:                 
                         self.r = 0
                         sleep(1)
                         self.ser.close()
                         break
                     except:
                         break
                 self.Destroy()
             else:
                 e.Veto()
             
        
def main():
     app = wx.App()
     GUI(None)
     app.MainLoop()

if __name__=='__main__':
     main()