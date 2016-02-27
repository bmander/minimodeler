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

        self.front.bind("<B1-Motion>", self.on_front_move)
        self.front.bind("<Shift-Button-1>", self.on_front_shift_click)
        self.front.bind("<Button-1>", self.on_front_click)
        self.front.bind("<ButtonRelease-1>", self.on_buttonrelease)

        self.top.bind("<B1-Motion>", self.on_top_move)
        self.top.bind("<Button-1>", self.on_top_click)
        self.top.bind("<ButtonRelease-1>", self.on_buttonrelease)

        self.right.bind("<B1-Motion>", self.on_right_move)
        self.right.bind("<Button-1>", self.on_right_click)
        self.right.bind("<ButtonRelease-1>", self.on_buttonrelease)

        self.selected_ids = []

        self.points = []
        self.front_pts = {}
        self.top_pts = {}
        self.right_pts = {}

    def update_point_position(self,pt):
        self.front.coords( pt.ids[self.front], pt.x-2.5, pt.y-2.5, pt.x+2.5, pt.y+2.5 )
        self.top.coords( pt.ids[self.top], pt.x-2.5, pt.z-2.5, pt.x+2.5, pt.z+2.5 )
        self.right.coords( pt.ids[self.right], pt.z-2.5,pt.y-2.5,pt.z+2.5,pt.y+2.5 )

    def on_front_move(self, event):
        for id in self.selected_ids:
            pt = self.front_pts[id]
            pt.x = event.x
            pt.y = event.y

            self.update_point_position(pt)

    def on_top_move(self, event):
        for id in self.selected_ids:
            pt = self.top_pts[id]
            pt.x = event.x
            pt.z = event.y

            self.update_point_position(pt)

    def on_right_move(self, event):
        for id in self.selected_ids:
            pt = self.top_pts[id]
            pt.z = event.x
            pt.y = event.y

            self.update_point_position(pt)

    def on_front_click(self,event):
        self.selected_ids = self.front.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)

    def on_top_click(self,event):
        self.selected_ids = self.top.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)

    def on_right_click(self,event):
        self.selected_ids = self.right.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)

    def on_front_shift_click(self,event):
        pt = Point(event.x,event.y,0)
        self.points.append( pt )

        frontid = self.front.create_rectangle(pt.x-2.5,pt.y-2.5,pt.x+2.5,pt.y+2.5)
        topid = self.top.create_rectangle(pt.x-2.5,pt.z-2.5,pt.x+2.5,pt.z+2.5)
        rightid = self.right.create_rectangle(pt.z-2.5,pt.y-2.5,pt.z+2.5,pt.y+2.5)

        pt.ids[self.front] = frontid
        pt.ids[self.top] = topid
        pt.ids[self.right] = rightid

        self.front_pts[frontid] = pt
        self.top_pts[topid] = pt
        self.right_pts[rightid] = pt

    def on_buttonrelease(self,event):
        self.selected_points = []

master = Tk()
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
