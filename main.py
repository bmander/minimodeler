from Tkinter import *

class App:
    def __init__(self,master):

        self.front = Canvas(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.front.place(x=5,y=310)

        self.top = Canvas(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.top.place(x=5,y=5)

        self.right = Canvas(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.right.place(x=310,y=310)

        self.px,self.py=None,None

        self.front.bind("<B1-Motion>", self.on_move)
        self.front.bind("<Button-1>", self.on_click)

    def on_move(self, event):

        if self.px is not None and self.py is not None:
            self.front.create_line(self.px,self.py,event.x,event.y)
            self.top.create_line(self.px,self.py,event.x,event.y)
            self.right.create_line(self.px,self.py,event.x,event.y)

        self.px = event.x
        self.py = event.y

    def on_click(self,event):
        self.front.delete("all")
        self.px,self.py=event.x,event.y

master = Tk()
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
