from Tkinter import *

class App:
    def __init__(self,master):

        self.w = Canvas(master, width=200, height=100)
        self.w.pack()

        self.w.create_line(0, 0, 200, 100)
        self.w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

        self.w.create_rectangle(50, 25, 150, 75, fill="blue")

        self.px,self.py=None,None

        self.w.bind("<B1-Motion>", self.callback)

    def callback(self, event):
        if self.px is not None and self.py is not None:
            self.w.create_line(self.px,self.py,event.x,event.y)

        #print "clicked at", event.x, event.y
        self.px = event.x
        self.py = event.y

master = Tk()
app = App(master)

mainloop()
