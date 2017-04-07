import serial
from Tkinter import *
from PIL import ImageTk
import Pmw

intensity = ("5 mW", "7.5 mW", "10 mW", "12.5 mW", "15 mW")

if __name__ == '__main__':
   root = Tk()
   root.title('FNIRS software')
   w = Canvas(root, width = 246, height = 206)
   im = ImageTk.PhotoImage(file = "D:\\images\\body.bmp")
   w.create_image(123, 103, image = im)
   w.grid(row=0, column=0, sticky=NW)
   combobox = Pmw.ComboBox(root, label_text='Intensity: ', labelpos='wn', listbox_width=15,
            dropdown=1, selectioncommand=serial, scrolledlist_items=intensity)
   combobox.grid(row=0, column=0, padx=5, pady=250, sticky=W)  
   combobox.selectitem(intensity[1])
   Button(root, text='start').grid(row=10, column=0, padx=10, pady=10, sticky=SW) 
   Button(root, text='Quit', command=quit).grid(row=10, column=0, padx=0, pady=10, sticky=S)
   f=Frame(root, bd=2, relief=RAISED)
   c = Canvas(f, width=300, height=300)
   im1 = ImageTk.PhotoImage(file="D:\\images\\nirs.bmp")
   c.create_image(150, 150, image=im1)
   c.grid(row=0, column=0, sticky=N)
   f.grid(row=0, column=2, sticky=NE)
   mainloop()