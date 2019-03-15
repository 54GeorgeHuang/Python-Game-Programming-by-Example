import sys
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Light(object):
    enabled = False
    colors = [(1.,1.,1.,1.), (1.,0.5,0.5,1.),
              (0.5,1.,0.5,1.), (0.5,0.5,1.,1.)]

    def __init__(self, light_id, position):
        self.light_id = light_id
        self.position = position
        self.current_color = 0

    def render(self):
        light_id = self.light_id
        color = Light.colors[self.current_color]
        glLightfv(light_id, GL_POSITION, self.position)
        glLightfv(light_id, GL_DIFFUSE, color)
        glLightfv(light_id, GL_CONSTANT_ATTENUATION, 0.1)
        glLightfv(light_id, GL_LINEAR_ATTENUATION, 0.05)

    def switch_color(self):
        self.current_color += 1
        self.current_color %= len(Light.colors)
        
    def enable(self):
        if not Light.enabled:
            glEnable(GL_LIGHTING)
            Light.enabled = True
        glEnable(self.light_id)


class Sphere(object):
    slices = 40
    stacks = 40
    
    def __init__(self, radius, position, color):
        self.radius = radius
        self.position = position
        self.color = color

    def render(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.color)
        glutSolidSphere(self.radius, Sphere.slices, Sphere.stacks)
        glPopMatrix()


class App(object):
    def __init__(self, width=800, height=600):
        self.title = b'OpenGL demo'
        self.width = width
        self.height = height
        self.angle = 0
        self.distance = 20
        self.light = Light(GL_LIGHT0, (15, 5, 15, 1))
        self.sphere1 = Sphere(2, (0, 0, 0), (1, 1, 1, 1))
        self.sphere2 = Sphere(1, (4, 2, 0), (1, 0.4, 0.4, 1))

    def start(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowPosition(50, 50)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(self.title)

        glEnable(GL_DEPTH_TEST)
        self.light.enable()
        
        glClearColor(.1, .1, .1, 1)
        glMatrixMode(GL_PROJECTION)
        aspect = self.width / self.height
        gluPerspective(40., aspect, 1., 40.)
        glMatrixMode(GL_MODELVIEW)
        
        glutDisplayFunc(self.display)
        glutSpecialFunc(self.keyboard)
        glutMainLoop()

    def display(self):
        x = math.sin(self.angle) * self.distance
        z = math.cos(self.angle) * self.distance

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(x, 0, z,
                  0, 0, 0,
                  0, 1, 0)

        self.light.render()
        self.sphere1.render()
        self.sphere2.render()

        glutSwapBuffers()

    def keyboard(self, key, x, y):
        if key == GLUT_KEY_INSERT:
            sys.exit()
        if key == GLUT_KEY_UP:
            self.distance -= 0.1
        if key == GLUT_KEY_DOWN:
            self.distance += 0.1
        if key == GLUT_KEY_LEFT:
            self.angle -= 0.05
        if key == GLUT_KEY_RIGHT:
            self.angle += 0.05
        if key == GLUT_KEY_F1:
            self.light.switch_color()

        self.distance = max(10, min(self.distance, 20))
        self.angle %= math.pi * 2
        glutPostRedisplay()


if __name__ == '__main__':
    app = App()
    app.start()
