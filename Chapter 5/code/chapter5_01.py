import sys
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class App(object):
    def __init__(self, width=800, height=600):
        self.title = b'OpenGL demo'
        self.width = width
        self.height = height
        self.angle = 0
        self.distance = 20

    def start(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowPosition(50, 50)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(self.title)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glClearColor(.1, .1, .1, 1)
        glMatrixMode(GL_PROJECTION)
        aspect = self.width / self.height
        gluPerspective(40., aspect, 1., 40.)
        glMatrixMode(GL_MODELVIEW)

        glutDisplayFunc(self.display)
        glutSpecialFunc(self.keyboard)
        glutMainLoop()

    def keyboard(self, key, x, y):
        pass

    def display(self):
        x = math.sin(self.angle) * self.distance
        z = math.cos(self.angle) * self.distance

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(x, 0, z,
                  0, 0, 0,
                  0, 1, 0)

        glLightfv(GL_LIGHT0, GL_POSITION, [15, 5, 15, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1., 1., 1., 1.])
        glLightfv(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightfv(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1., 1., 1., 1.])
        glutSolidSphere(2, 40, 40)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(4, 2, 0)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.,0.4,0.4,1.0])
        glutSolidSphere(1, 40, 40)
        glPopMatrix()

        glutSwapBuffers()


if __name__ == '__main__':
    app = App()
    app.start()
