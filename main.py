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

def make_rotation_matrix(theta_x,theta_y,theta_z):
    A_x = np.array([[1,0,0],
                    [0,np.cos(theta_x),-np.sin(theta_x)],
                    [0,np.sin(theta_x),np.cos(theta_x)]])
    A_y = np.array([[np.cos(theta_y),0,np.sin(theta_y)],
                    [0,1,0],
                    [-np.sin(theta_y),0,np.cos(theta_y)]])
    A_z = np.array([[np.cos(theta_z),-np.sin(theta_z),0],
                    [np.sin(theta_z),np.cos(theta_z),0],
                    [0,0,1]])

    return np.dot( np.dot(A_x,A_y), A_z )

class Viewport(Canvas):
    def __init__(self, *args, **kwargs):
        self.pts = {}
        Canvas.__init__(self,*args,**kwargs)

    def set_euler_angles(self,theta_x,theta_y,theta_z):
        self.theta = np.array([theta_x,theta_y,theta_z], dtype=np.float32)

        self._update_rot_matrices()

    def rotate(self,theta_x,theta_y,theta_z):
        self.theta += [theta_x,theta_y,theta_z]

        self._update_rot_matrices()

    def _update_rot_matrices(self):
        self.rot_matrix = make_rotation_matrix(*self.theta)
        self.rev_rot_matrix = make_rotation_matrix(*(-self.theta))

    def update_point(self,id):
        pt = self.pts[id]
        x,y,z = self.proj(pt)

        x,y = self.to_cartesian(x,y)
        self.coords( id, x-2.5, y-2.5, x+2.5, y+2.5 )

    def update_all_points(self):
        for id in self.pts:
            self.update_point(id)

    def add_point(self,pt):
        x,y,z = self.proj(pt)

        x,y = self.to_cartesian(x,y)
        id = self.create_rectangle( x-2.5, y-2.5, x+2.5, y+2.5 )

        self.pts[id] = pt

        return id

    def proj(self,pt):
        # convert world-space 3d coordinates to 3d point oriented to screen
        return np.dot(self.rot_matrix,pt.s)

    def reverse_proj(self,x,y,z=0):
        # convert 2d screen coordinates into 3d coordinate, with z coordinate set to zero
        s = np.array([x,y,z])
        return np.dot( self.rev_rot_matrix, s )

    def to_cartesian(self,x,y):
        return x, self.winfo_reqheight()-y;

class App:
    def __init__(self,master):
        self.master = master

        self.front = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.front.set_euler_angles( 0,0,0 )
        self.front.place(x=5,y=310)

        self.top = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.top.set_euler_angles( -np.pi/2,0,0 )
        self.top.place(x=5,y=5)

        self.right = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.right.set_euler_angles( 0,np.pi/2,0 )
        self.right.place(x=310,y=310)

        self.pers = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.pers.set_euler_angles( 0,0,0 )
        self.pers.place(x=310,y=5)

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

        self.pers.bind("<Button-1>", self.pers_click)
        self.pers.bind("<ButtonRelease-1>", self.pers_clickrelease)
        self.pers.bind("<B1-Motion>", self.pers_motion)

        self.selected_ids = []

        self.points = []

    def pers_click(self,event):
        self.persdown = (event.x,event.y)

    def pers_clickrelease(self,event):
        self.persdown = None

    def pers_motion(self,event):
        beta = 0.01*(event.x - self.persdown[0])
        alpha = 0.01*(event.y - self.persdown[1])

        self.pers.rotate(alpha,beta,0)
        self.pers.update_all_points()

        self.persdown = (event.x,event.y)

    def update_point_position(self,pt):
        self.front.update_point( pt.ids[self.front] )
        self.top.update_point( pt.ids[self.top] )
        self.right.update_point( pt.ids[self.right] )
        self.pers.update_point( pt.ids[self.pers] )

    def add_new_point(self,pt):
        frontid = self.front.add_point(pt)
        topid = self.top.add_point(pt)
        rightid = self.right.add_point(pt)
        persid = self.pers.add_point(pt)

        pt.ids[self.front] = frontid
        pt.ids[self.top] = topid
        pt.ids[self.right] = rightid
        pt.ids[self.pers] = persid

    def on_move(self, event):
        for id in self.selected_ids:
            pt = event.widget.pts[id]

            px,py,pz = event.widget.proj(pt) #we need the screen-oriented depth coord 'pz'

            x,y = event.widget.to_cartesian(event.x,event.y)

            pt.s = event.widget.reverse_proj( x, y, pz )

            self.update_point_position(pt)

    def on_click(self,event):
        self.selected_ids = event.widget.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)

    def on_shift_click(self,event):
        x,y = event.widget.to_cartesian(event.x,event.y)
        pt = event.widget.reverse_proj(x,y)

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
