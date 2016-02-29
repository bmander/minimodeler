from Tkinter import *
import numpy as np

class Point:
    def __init__(self,x,y,z,color="black"):
        self.s = [x,y,z]
        self.color = color
        self.viewports = {} # viewport -> id

    def add_viewport(self,viewport):
        self.viewports[viewport] = None

    @property
    def x(self):
        return self.s[0]

    @property
    def y(self):
        return self.s[1]

    @property
    def z(self):
        return self.s[2]

    def add_to_viewport(self, viewport):
        if self.viewports.get(viewport) is not None:
            raise Exception( "this point has already been added to this viewport" )

        px,py,pz = viewport.proj(*self.s) #point oriented to viewport
        pt = viewport.to_viewport(px,py,pz) #get canvas coordinates
        if pt is None:
            self.viewports[viewport] = None
            return

        cx,cy = pt
        id = viewport.create_rectangle( cx-2.5, cy-2.5, cx+2.5, cy+2.5, outline=self.color )
        self.viewports[viewport] = id

        viewport.pts[id] = self

class Camera(Point):
    pass

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
        self.width = kwargs['width']
        self.height = kwargs['height']

        self.f = kwargs.get("f")
        if 'f' in kwargs:
            del kwargs['f']

        self.set_camera_position(0,0,0)

        Canvas.__init__(self,*args,**kwargs)

    def set_euler_angles(self,theta_x,theta_y,theta_z):
        self.theta = np.array([theta_x,theta_y,theta_z], dtype=np.float32)

        self._update_rot_matrices()

    def set_camera_position(self,x,y,z):
        self.camera_pos = np.array([x,y,z], dtype=np.float32)

    def rotate(self,theta_x,theta_y,theta_z):
        self.theta += [theta_x,theta_y,theta_z]

        self._update_rot_matrices()

    def pan(self,x,y,z,relative=False):
        s = np.array([x,y,z], dtype=np.float32)
        if relative:
            s = np.dot( self.rev_rot_matrix, s )

        self.camera_pos += s

    def _update_rot_matrices(self):
        self.rot_matrix = make_rotation_matrix(*self.theta)
        self.rev_rot_matrix = make_rotation_matrix(*(-self.theta))

    def update_point(self,id):
        pt = self.pts[id]
        x,y,z = self.proj(*pt.s)

        coord = self.to_viewport(x,y,z)
        if coord is None:
            return
        x,y = coord
        self.coords( id, x-2.5, y-2.5, x+2.5, y+2.5 )

    def update_all_points(self):
        for id in self.pts:
            self.update_point(id)

    # def add_point(self,pt):
    #     x,y,z = self.proj(pt)
    #
    #     coord = self.to_viewport(x,y,z)
    #     if coord is None:
    #         return
    #     x,y = coord
    #     id = self.create_rectangle( x-2.5, y-2.5, x+2.5, y+2.5, outline=pt.color )
    #
    #     self.pts[id] = pt
    #
    #     return id

    def proj(self,x,y,z):
        # convert world-space 3d coordinates to camera coordinates
        screen_pt = np.dot(self.rot_matrix,[x,y,z])

        # rotate camera position to sit on the z axis
        aligned_camera = np.dot(self.rot_matrix,self.camera_pos)

        camera_oriented_pt = screen_pt - aligned_camera

        return camera_oriented_pt

    def reverse_proj(self,x,y,z=0):
        # convert 3d camera-oriented coordinates into world coordinates
        s = np.array([x,y,z]) + self.camera_pos

        return np.dot( self.rev_rot_matrix, s )

    def to_viewport(self,x,y,z):
        if self.f is not None:
            if z<0:
                return None #point behind camera

            x = self.f/z * x
            y = self.f/z * y

        # convert from screen-oriented 3d points to viewport coordinates
        return self.width/2 + x, self.height/2 - y

    def from_viewport(self,x,y):
        if self.f is not None:
            raise Exception("can't do this from a perspective viewport")

        # convert viewport coordinates to screen-oriented x and y coords
        return x - self.width/2, self.height/2 - y

class App:
    def __init__(self,master):
        self.master = master

        self.front = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.front.set_camera_position( 0,0,0 )
        self.front.set_euler_angles( 0,0,0 )
        self.front.place(x=5,y=310)

        self.top = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.top.set_euler_angles( -np.pi/2,0,0 )
        self.top.place(x=5,y=5)

        self.right = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.right.set_euler_angles( 0,np.pi/2,0 )
        self.right.place(x=310,y=310)

        self.pers = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1,f=400.0)
        self.pers.set_euler_angles( 0,0,0 )
        self.pers.set_camera_position(0, 0, -100.0)
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
        self.pers.bind_all("<+>", self.press_plus)
        self.pers.bind_all("<minus>", self.press_minus)
        self.pers.bind_all("<Left>", self.press_left)
        self.pers.bind_all("<Right>", self.press_right)
        self.pers.bind_all("<Up>", self.press_up)
        self.pers.bind_all("<Down>", self.press_down)

        self.selected_id = None

        self.points = []

        # sample cube
        for x in [-10,10]:
            for y in [-10,10]:
                for z in [-10,10]:
                    self.add_new_point( Point(x,y,z) )

        # camera points
        self.add_new_point( Camera(0,0,-100, color="red") )


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
        self.front.update_point( pt.viewports[self.front] )
        self.top.update_point( pt.viewports[self.top] )
        self.right.update_point( pt.viewports[self.right] )
        self.pers.update_point( pt.viewports[self.pers] )

    def add_new_point(self,pt):
        pt.add_to_viewport( self.front )
        pt.add_to_viewport( self.top )
        pt.add_to_viewport( self.right )
        pt.add_to_viewport( self.pers )

    def on_move(self, event):
        if self.selected_id is None:
            return

        pt = event.widget.pts[self.selected_id]

        if isinstance(pt,Camera):
            self.pers.set_camera_position(pt.x, pt.y, pt.z)
            self.pers.update_all_points()

        px,py,pz = event.widget.proj(*pt.s) #we need the screen-oriented depth coord 'pz'

        x,y = event.widget.from_viewport(event.x,event.y)

        pt.s = event.widget.reverse_proj( x, y, pz )

        self.update_point_position(pt)

    def on_click(self,event):
        ix = event.widget.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)
        self.selected_id = ix[0] if len(ix)>0 else None

    def on_shift_click(self,event):
        x,y = event.widget.from_viewport(event.x,event.y)
        pt = event.widget.reverse_proj(x,y)

        pt = Point(*pt)
        self.points.append( pt )

        self.add_new_point(pt)

    def on_buttonrelease(self,event):
        self.selected_id = None

    def press_plus(self,event):
        self.pers.f *= 1.5
        self.pers.update_all_points()

    def press_minus(self,event):
        self.pers.f *= 0.75
        self.pers.update_all_points()

    def press_left(self,event):
        self.pers.pan(-5,0,0, relative=False)
        self.pers.update_all_points()

    def press_right(self,event):
        self.pers.pan(5,0,0, relative=False)
        self.pers.update_all_points()

    def press_up(self,event):
        self.pers.pan(0,5,0, relative=False)
        self.pers.update_all_points()

    def press_down(self,event):
        self.pers.pan(0,-5,0, relative=False)
        self.pers.update_all_points()

master = Tk()
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
