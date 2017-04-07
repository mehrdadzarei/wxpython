import serial
from Tkinter import *
import Pmw, time

def run():
   def read_serial():
         while True:
            c = ser.read() # attempt to read a character from Serial
        
            #was anything read?
            if len(c) == 0:
               break
        
            # get the buffer from outside of this function
            global serBuffer
        
            # check if character is a delimeter
            if c == '\r':
               c = '' # don't want returns. chuck it
            
            if c == '\n':
               serBuffer += "\n" # add the newline to the buffer
            
               #add the line to the TOP of the log
               text.appendtext(serBuffer)   # for set the scrollbar end of text, should use appendtext no insert
               serBuffer = "" # empty the buffer
            else:
               serBuffer += c # add to the buffer
         f.after(10, read_serial) # check serial again soon, this is for update root
   f.after(10, read_serial) # check serial again soon
def play(event):
   c = com.get()
   ser.port = c
   b = int(baud.get())
   ser.baudrate = b
   ser.open()
   run()
   
def pause(event):
     ser.close()
   
def load(event):
      text.importfile('%s' %var.get())
   
def clear(event):
      text.clear()

def save(event):
     text.exportfile('%s'%var.get())   

def ext(event):
     quit()

baudrate = ("300", "1200", "2400", "4800", "9600", "19200",
           "38400", "57600", "115200", "230400", "250000")
comnumber = ("com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8"
            , "com9", "com10", "com11", "com12", "com13", "com14", "com15", "com16"
            , "com17", "com18", "com19", "com20", "com21", "com22", "com23", "com24")
serBuffer = ""
ser = serial.Serial(timeout=0, writeTimeout=0)

if __name__ == '__main__':
   root = Tk()
   root.title('Terminal')
   f = Frame(root)
   text = Pmw.ScrolledText(f, borderframe=1, usehullsize=0, text_wrap='none')
   text.pack(side=TOP, fill=BOTH, expand=1)
   f.pack(side=TOP, fill=BOTH, expand=1)
   f1 = Frame(f)
   Label(f1, text='Path:').pack(side=LEFT, anchor=W, padx=0, pady=5, expand=1)
   var = StringVar()
   Entry(f1, textvariable=var).pack(side=LEFT, anchor=W, padx=0, pady=5, expand=1)
   f1.pack(side=LEFT, anchor=NW, pady=5, expand=0)
   var.set("D:\\...\\name.txt")
   entry = Frame(f)
   com = Pmw.ComboBox(entry, label_text='Port NO.: ', labelpos='w', listbox_width=0,
            dropdown=1, scrolledlist_items=comnumber)
   com.pack(side=LEFT, anchor=E, padx=10, pady=5, expand=1)
   com.selectitem(comnumber[2])
   baud = Pmw.ComboBox(entry, label_text='Baud Rate: ', labelpos='w', listbox_width=0,
            dropdown=1, scrolledlist_items=baudrate)
   baud.pack(side=RIGHT, anchor=E, padx=10, pady=5, expand=1)
   baud.selectitem(baudrate[4])
   entry.pack(side=RIGHT, anchor=E,  pady=5, expand=0)
   f2 = Frame(root)
   start = Frame(f2)
   button1 = Button(start, text='Start', takefocus=1)  # tackefocuse=1 is for wheel of Tab key
   button1.bind('<Button-1>', play)
   button1.bind('<KeyPress-Return>', play)
   button1.pack(side=LEFT, padx=5, pady=5,ipadx=10, expand=1)
   button2 = Button(start, text='Stop')
   button2.bind('<Button-1>', pause)
   button2.bind('<KeyPress-Return>', pause)
   button2.pack(side=LEFT, padx=5, pady=5,ipadx=10, expand=1)
   start.pack(side=LEFT, anchor=W,  pady=5, expand=1)
   sav = Frame(f2)
   button3 = Button(sav, text='Save')
   button3.bind('<Button-1>', save)
   button3.bind('<KeyPress-Return>', save)
   button3.pack(side=LEFT, padx=5, pady=5,ipadx=10, expand=1)
   button4 = Button(sav, text='Load')
   button4.bind('<Button-1>', load)
   button4.bind('<KeyPress-Return>', load)
   button4.pack(side=LEFT, padx=5, pady=5,ipadx=10, expand=1)
   button5 = Button(sav, text='Clear')
   button5.bind('<Button-1>', clear)
   button5.bind('<KeyPress-Return>', clear)
   button5.pack(side=LEFT, padx=5, pady=5,ipadx=10, expand=1)
   sav.pack(side=LEFT, anchor=W, padx=50, pady=5, expand=1)                
   button6 = Button(f2, text='Quit')
   button6.bind('<Button-1>', ext)
   button6.bind('<KeyPress-Return>', ext)
   button6.pack(side=RIGHT, anchor=E, padx=5,pady=5, ipadx=10, expand=1)
   f2.pack(side=LEFT, pady=5, ipadx=100, anchor=W, fill=BOTH)
   button1.focus_set()
   root.mainloop()