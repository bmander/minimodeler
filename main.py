from Tkinter import *
import numpy as np

class Point:
    def __init__(self,x,y,z):
        self.s = [x,y,z]
        self.ids = {}

    @property
    def x(self):
        return self.s[0]

    @property
    def y(self):
        return self.s[1]

    @property
    def z(self):
        return self.s[2]

class Viewport(Canvas):
    def __init__(self, *args, **kwargs):
        self.pts = {}
        Canvas.__init__(self,*args,**kwargs)

    def set_dim_map(self,x,y):
        self.x_dim = x
        self.y_dim = y

    def set_proj_matrix(self,A):
        self.proj_matrix = A

    def set_euler_angles(self,theta_x,theta_y,theta_z):
        self.theta = np.array([theta_x,theta_y,theta_z])
        A_x = np.array([[1,0,0],
                        [0,np.cos(theta_x),-np.sin(theta_x)],
                        [0,np.sin(theta_x),np.cos(theta_x)]])
        A_y = np.array([[np.cos(theta_y),0,np.sin(theta_y)],
                        [0,1,0],
                        [-np.sin(theta_y),0,np.cos(theta_y)]])
        A_z = np.array([[np.cos(theta_z),-np.sin(theta_z),0],
                        [np.sin(theta_z),np.cos(theta_z),0],
                        [0,0,1]])

        self.rot_matrix = np.dot( np.dot(A_x,A_y), A_z )

    def update_point(self,id):
        pt = self.pts[id]
        projpt = self.proj(pt)

        self.coords( id, projpt[0]-2.5, projpt[1]-2.5, projpt[0]+2.5, projpt[1]+2.5 )

    def add_point(self,pt):
        projpt = self.proj(pt)

        id = self.create_rectangle( projpt[0]-2.5, projpt[1]-2.5, projpt[0]+2.5, projpt[1]+2.5 )

        self.pts[id] = pt

        return id

    def proj(self,pt):
        # convert world-space 3d coordinates to screen 2d coordinates
        rotated_point = np.dot(self.rot_matrix,pt.s)

        return rotated_point[[0,1]]

    def reverse_proj(self,x,y):
        # convert 2d screen coordinates into 3d coordinate, with z coordinate set to zero
        return np.dot( self.proj_matrix.T, np.array([x,y]) )

class App:
    def __init__(self,master):
        self.master = master

        self.front = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.front.set_dim_map(0,1) # x maps to the 0th dimension, y maps to the 1st dimension
        self.front.set_proj_matrix( np.array([[1,0,0],[0,1,0]]) )
        self.front.set_euler_angles( 0,0,0 )
        self.front.place(x=5,y=310)

        self.top = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.top.set_dim_map(0,2) # x maps to the 0th dimension, y maps to the 2nd dimension
        self.top.set_proj_matrix( np.array([[1,0,0],[0,0,1]]) )
        self.top.set_euler_angles( -np.pi/2,0,0 )
        self.top.place(x=5,y=5)

        self.right = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.right.set_dim_map(2,1) # x maps to the 2nd dimension, y maps to the 2nd dimension
        self.right.set_proj_matrix( np.array([[0,0,1],[0,1,0]]) )
        self.right.set_euler_angles( 0,np.pi/2,0 )
        self.right.place(x=310,y=310)

        self.front.bind("<B1-Motion>", self.on_move)
        self.front.bind("<Shift-Button-1>", self.on_shift_click)
        self.front.bind("<Button-1>", self.on_click)
        self.front.bind("<ButtonRelease-1>", self.on_buttonrelease)

        self.top.bind("<B1-Motion>", self.on_move)
        self.top.bind("<Shift-Button-1>", self.on_shift_click)
        self.top.bind("<Button-1>", self.on_click)
        self.top.bind("<ButtonRelease-1>", self.on_buttonrelease)

        self.right.bind("<B1-Motion>", self.on_move)
        self.right.bind("<Shift-Button-1>", self.on_shift_click)
        self.right.bind("<Button-1>", self.on_click)
        self.right.bind("<ButtonRelease-1>", self.on_buttonrelease)

        self.selected_ids = []

        self.points = []

    def update_point_position(self,pt):
        self.front.update_point( pt.ids[self.front] )
        self.top.update_point( pt.ids[self.top] )
        self.right.update_point( pt.ids[self.right] )

    def add_new_point(self,pt):
        frontid = self.front.add_point(pt)
        topid = self.top.add_point(pt)
        rightid = self.right.add_point(pt)

        pt.ids[self.front] = frontid
        pt.ids[self.top] = topid
        pt.ids[self.right] = rightid

    def on_move(self, event):
        for id in self.selected_ids:
            pt = event.widget.pts[id]
            pt.s[ event.widget.x_dim ] = event.x
            pt.s[ event.widget.y_dim ] = event.y

            self.update_point_position(pt)

    def on_click(self,event):
        self.selected_ids = event.widget.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)

    def on_shift_click(self,event):
        pt = event.widget.reverse_proj(event.x,event.y)

        pt = Point(*pt)
        self.points.append( pt )

        self.add_new_point(pt)

    def on_buttonrelease(self,event):
        self.selected_points = []

master = Tk()
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
