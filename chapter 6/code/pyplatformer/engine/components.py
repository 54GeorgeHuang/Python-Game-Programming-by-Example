from OpenGL.GL import *
from OpenGL.GLU import *


__all__ = ['Component', 'Renderable', 'Cube', 'Sphere', 'Light', 'Camera']


class Component(object):
    __slots__ = ['gameobject']

    def start(self):
        pass

    def update(self, dt):
        pass

    def stop(self):
        pass

    def on_collide(self, other, contacts):
        pass


class Renderable(Component):
    __slots__ = ['color']
    
    def __init__(self, color):
        self.color = color

    def render(self):
        pos = self.gameobject.position
        rot = self.gameobject.rotation
        scale = self.gameobject.scale
        glPushMatrix()
        glTranslatef(*pos)
        if rot != (0, 0, 0):
            glRotatef(rot[0], 1, 0, 0)
            glRotatef(rot[1], 0, 1, 0)
            glRotatef(rot[2], 0, 0, 1)
        if scale != (1, 1, 1):
            glScalef(*scale)
        if self.color is not None:
            glColor4f(*self.color)
        self._render()
        glPopMatrix()

    def _render(self):
        pass


class Light(Renderable):
    def __init__(self, light_id, color=(1, 1, 1, 0),
                 constant_att=0.1, linear_att=0.05):
        self.light_id = light_id
        self.enabled = False
        self.color = color
        self.constant_att = constant_att
        self.linear_att = linear_att

    def render(self):
        if not self.enabled:
            self.enabled = True
            glEnable(self.light_id)
        light_id = self.light_id
        position = self.gameobject.position
        glLightfv(light_id, GL_POSITION, position)
        glLightfv(light_id, GL_DIFFUSE, self.color)
        glLightfv(light_id, GL_CONSTANT_ATTENUATION, self.constant_att)
        glLightfv(light_id, GL_LINEAR_ATTENUATION, self.linear_att)


class Camera(Component):
    instance = None

    def __init__(self, dy, dz):
        self.dy = dy
        self.dz = dz
        Camera.instance = self

    def render(self):
        pos = self.gameobject.position
        glLoadIdentity()
        gluLookAt(pos[0], self.dy, self.dz,
                  pos[0], pos[1], pos[2],
                  0, 1, 0)


class Cube(Renderable):
    sides = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
             (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))

    normals = ((0, 0, -1), (-1, 0, 0), (0, 0, 1),
               (1, 0, 0), (0, 1, 0), (0, -1, 0))
    
    def __init__(self, color, size):
        super(Cube, self).__init__(color)
        x, y, z = map(lambda i: i/2, size)
        self.vertices = (
            (x, -y, -z), (x, y, -z),
            (-x, y,-z), (-x, -y, -z),
            (x, -y, z), (x, y, z),
            (-x, -y, z), (-x, y,  z))

    def _render(self):
        glBegin(GL_QUADS)
        for i, side in enumerate(Cube.sides):
            glNormal3fv(Cube.normals[i])
            for v in side:
                glVertex3fv(self.vertices[v])
        glEnd()


class Sphere(Renderable):
    slices = 40
    stacks = 40
    
    def __init__(self, radius, color):
        super(Sphere, self).__init__(color)
        self.radius = radius
        self.quadratic = gluNewQuadric()

    def _render(self):
        gluSphere(self.quadratic, self.radius,
                  Sphere.slices, Sphere.stacks)
