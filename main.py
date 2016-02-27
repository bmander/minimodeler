from Tkinter import *

class Point:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.ids = {}

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
        self.front.bind("<Shift-Button-1>", self.on_front_shift_click)
        self.front.bind("<Button-1>", self.on_front_click)

        self.selected_ids = []

        self.points = []
        self.front_pts = {}
        self.top_pts = {}
        self.right_pts = {}

    def set_selected_pt_coords(self,x=None,y=None,z=None):
        for id in self.selected_ids:
            # pt = self.points[int(tag)]
            # pt[0] = pt[0] or x
            # pt[1] = pt[1] or y
            # pt[2] = pt[2] or z

            self.front.coords(id, x-2.5,y-2.5,x+2.5,y+2.5)

    def on_move(self, event):
        for id in self.selected_ids:
            pt = self.front_pts[id]
            pt.x = event.x
            pt.x = event.y

        self.set_selected_pt_coords(event.x,event.y)

    def on_front_click(self,event):
        ids = [x for x in self.front.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)]

        self.selected_ids = ids

    def on_front_shift_click(self,event):
        ix = len(self.points)
        pt = Point(event.x,event.y,0)
        self.points.append( pt )

        frontid = self.front.create_rectangle(pt.x-2.5,pt.y-2.5,pt.x+2.5,pt.y+2.5)
        topid = self.top.create_rectangle(pt.x-2.5,pt.z-2.5,pt.x+2.5,pt.z+2.5)

        pt.ids[self.front] = frontid
        pt.ids[self.top] = topid

        self.front_pts[frontid] = pt
        self.top_pts[topid] = pt

    def on_buttonrelease(self,event):
        self.selected_points = []

master = Tk()
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
