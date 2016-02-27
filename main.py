from Tkinter import *

class App:
    def __init__(self,master):
        self.master = master

        self.front = Canvas(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.front.place(x=5,y=310)

        self.top = Canvas(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.top.place(x=5,y=5)

        self.right = Canvas(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.right.place(x=310,y=310)

        self.front.bind("<B1-Motion>", self.on_move)

        self.front.bind("<ButtonRelease-1>", self.on_buttonrelease)
        self.front.bind("<Shift-Button-1>", self.on_shift_click)
        self.front.bind("<Button-1>", self.on_click)

        self.selected_points = None

    def on_move(self, event):

        if self.selected_points is not None:
            for point in self.selected_points:
                self.front.coords(point, event.x-2.5,event.y-2.5,event.x+2.5,event.y+2.5)

    def on_click(self,event):
        self.selected_points = self.front.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)

    def on_shift_click(self,event):
        self.front.create_rectangle(event.x-2.5,event.y-2.5,event.x+2.5,event.y+2.5)

    def on_buttonrelease(self,event):
        self.selected_points = None

master = Tk()
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
