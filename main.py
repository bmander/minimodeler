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

        coord = viewport.world_to_viewport(*self.s)
        if coord is None:
            self.viewports[viewport] = None
            return

        cx,cy = coord
        id = viewport.create_rectangle( cx-2.5, cy-2.5, cx+2.5, cy+2.5, outline=self.color )

        self.viewports[viewport] = id
        viewport.pts[id] = self

    def update(self,viewport):
        id = self.viewports[viewport]

        coord = viewport.world_to_viewport(*self.s)
        if coord is None:
            return
        x,y = coord
        viewport.coords( id, x-2.5, y-2.5, x+2.5, y+2.5 )

    def update_all(self):
        for viewport in self.viewports:
            self.update(viewport)

class Camera(Point):
    def __init__( self, x,y,z, alpha, beta, gamma, pers ):
        Point.__init__(self,x,y,z,color="red")
        self.theta = np.array([alpha,beta,gamma],dtype=np.float32)
        self.xaxis = {}
        self.yaxis = {}
        self.zaxis = {}

        self.rot_matrix = make_rotation_matrix(*-self.theta)

        self.pers = pers

    def rotate( self, alpha, beta, gamma):
        self.theta += np.array([alpha,beta,gamma],dtype=np.float32)
        self.rot_matrix = make_rotation_matrix(*-self.theta)


    def add_to_viewport(self, viewport):
        if viewport == self.pers:
            return

        if self.viewports.get(viewport) is not None:
            raise Exception( "this point has already been added to this viewport" )

        coord = viewport.world_to_viewport(*self.s)
        if coord is None:
            self.viewports[viewport] = None
            return

        cx,cy = coord
        id = viewport.create_rectangle( cx-2.5, cy-2.5, cx+2.5, cy+2.5, outline=self.color )

        axis = np.dot(self.rot_matrix, np.array([20,0,0]))
        top = self.s+axis
        coord = viewport.world_to_viewport(*top)
        if coord:
            axisx,axisy = coord
            self.xaxis[viewport] = viewport.create_line(cx,cy,axisx,axisy, fill="red")

        axis = np.dot(self.rot_matrix, np.array([0,20,0]))
        top = self.s+axis
        coord = viewport.world_to_viewport(*top)
        if coord:
            axisx,axisy = coord
            self.yaxis[viewport] = viewport.create_line(cx,cy,axisx,axisy, fill="green")

        axis = np.dot(self.rot_matrix, np.array([0,0,20]))
        top = self.s+axis
        coord = viewport.world_to_viewport(*top)
        if coord:
            axisx,axisy = coord
            self.zaxis[viewport] = viewport.create_line(cx,cy,axisx,axisy, fill="blue")

        self.viewports[viewport] = id
        viewport.pts[id] = self

    def update(self,viewport):
        if viewport == self.pers:
            return

        id = self.viewports[viewport]

        coord = viewport.world_to_viewport(*self.s)
        if coord is None:
            return
        x,y = coord
        viewport.coords( id, x-2.5, y-2.5, x+2.5, y+2.5 )

        axis = np.dot(self.rot_matrix, np.array([20,0,0]))
        top = self.s+axis
        coord = viewport.world_to_viewport(*top)
        if coord:
            cx,cy = coord
            viewport.coords( self.xaxis[viewport], x,y, cx, cy )

        axis = np.dot(self.rot_matrix, np.array([0,20,0]))
        top = self.s+axis
        coord = viewport.world_to_viewport(*top)
        if coord:
            cx,cy = coord
            viewport.coords( self.yaxis[viewport], x,y, cx, cy )

        axis = np.dot(self.rot_matrix, np.array([0,0,20]))
        top = self.s+axis
        coord = viewport.world_to_viewport(*top)
        if coord:
            cx,cy = coord
            viewport.coords( self.zaxis[viewport], x,y, cx, cy )

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

    def set_orientation(self,theta_x,theta_y,theta_z):
        self.theta = np.array([theta_x,theta_y,theta_z], dtype=np.float32)

        self._update_rot_matrices()

    def set_camera_position(self,x,y,z):
        self.camera_pos = np.array([x,y,z], dtype=np.float32)

    def rotate(self,theta_x,theta_y,theta_z):
        self.theta += [theta_x,theta_y,theta_z]

        self._update_rot_matrices()

    def _update_rot_matrices(self):
        self.rot_matrix = make_rotation_matrix(*self.theta)
        self.rev_rot_matrix = make_rotation_matrix(*(-self.theta))

    def proj(self,x,y,z):
        # convert world-space 3d coordinates to camera coordinates
        screen_pt = np.dot(self.rot_matrix,[x,y,z]-self.camera_pos)

        return screen_pt

    def reverse_proj(self,x,y,z=0):
        # convert 3d camera-oriented coordinates into world coordinates
        s = np.array([x,y,z]) + self.camera_pos

        return np.dot( self.rev_rot_matrix, s )

    def world_to_viewport(self,x,y,z):
        return self.to_viewport( *self.proj(x,y,z) )

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
        self.front.set_orientation( 0,0,0 )
        self.front.place(x=5,y=310)

        self.top = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.top.set_orientation( -np.pi/2,0,0 )
        self.top.place(x=5,y=5)

        self.right = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1)
        self.right.set_orientation( 0,np.pi/2,0 )
        self.right.place(x=310,y=310)

        self.pers = Viewport(master, width=300, height=300, highlightbackground="black",highlightthickness=1,f=400.0)
        self.pers.set_orientation( 0,0,0 )
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
        self.pers.bind_all("<f>", self.press_f)

        self.selected_id = None

        self.points = []

        # sample cube
        for x in [-10,10]:
            for y in [-10,10]:
                for z in [-10,10]:
                    self.add_new_point( Point(x,y,z) )

        # camera points
        self.camera = Camera(0,0,-100, 0,0,0, self.pers)
        self.add_new_point( self.camera )


    def pers_click(self,event):
        self.persdown = (event.x,event.y)

    def pers_clickrelease(self,event):
        self.persdown = None

    def pers_motion(self,event):
        beta = 0.01*(event.x - self.persdown[0])
        alpha = 0.01*(event.y - self.persdown[1])

        self.pers.rotate(alpha,beta,0)
        self.update_all_points(self.pers)

        self.camera.rotate(alpha,beta,0)
        self.camera.update_all()

        self.persdown = (event.x,event.y)

    def add_new_point(self,pt):
        pt.add_to_viewport( self.front )
        pt.add_to_viewport( self.top )
        pt.add_to_viewport( self.right )
        pt.add_to_viewport( self.pers )

        self.points.append( pt )

    def update_all_points(self,viewport):
        for pt in self.points:
            pt.update( viewport )

    def on_move(self, event):
        if self.selected_id is None:
            return

        pt = event.widget.pts[self.selected_id]

        if isinstance(pt,Camera):
            self.pers.set_camera_position(pt.x, pt.y, pt.z)
            self.update_all_points(self.pers)

        px,py,pz = event.widget.proj(*pt.s) #we need the screen-oriented depth coord 'pz'

        x,y = event.widget.from_viewport(event.x,event.y)

        pt.s = event.widget.reverse_proj( x, y, pz )
        pt.update_all()

    def on_click(self,event):
        ix = event.widget.find_overlapping(event.x-2,event.y-2,event.x+2,event.y+2)
        self.selected_id = ix[0] if len(ix)>0 else None

    def on_shift_click(self,event):
        x,y = event.widget.from_viewport(event.x,event.y)
        pt = event.widget.reverse_proj(x,y)

        pt = Point(*pt)
        self.add_new_point(pt)

    def on_buttonrelease(self,event):
        self.selected_id = None

    def press_plus(self,event):
        self.pers.f *= 1.5
        self.update_all_points(self.pers)

    def press_minus(self,event):
        self.pers.f *= 0.75
        self.update_all_points(self.pers)

    def press_f(self,event):
        if self.pers.f is not None:
            self.pers.f = None
        else:
            self.pers.f = 400.0

        self.update_all_points(self.pers)

master = Tk()
master.wm_title("minimodeler")
master.resizable(width=False, height=False)
master.geometry('{}x{}'.format(620, 620))
app = App(master)

mainloop()
