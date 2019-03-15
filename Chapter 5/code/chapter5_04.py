import sys
import math

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


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
        self.quadratic = gluNewQuadric()

    def render(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.color)
        gluSphere(self.quadratic, self.radius, Sphere.slices, Sphere.stacks)
        glPopMatrix()


class App(object):
    def __init__(self, width=800, height=600):
        self.title = 'OpenGL demo'
        self.fps = 60
        self.width = width
        self.height = height
        self.angle = 0
        self.distance = 20
        self.light = Light(GL_LIGHT0, (15, 5, 15, 1))
        self.sphere1 = Sphere(2, (0, 0, 0), (1, 1, 1, 1))
        self.sphere2 = Sphere(1, (4, 2, 0), (1, 0.4, 0.4, 1))

    def start(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height),
                                OPENGL | DOUBLEBUF)
        pygame.display.set_caption(self.title)
        
        glEnable(GL_DEPTH_TEST)
        self.light.enable()
        
        glClearColor(.1, .1, .1, 1)
        glMatrixMode(GL_PROJECTION)
        aspect = self.width / self.height
        gluPerspective(40., aspect, 1., 40.)
        glMatrixMode(GL_MODELVIEW)

        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(self.fps)
            self.process_input(dt)
            self.display()

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
        pygame.display.flip()

    def process_input(self, dt):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quit()
                if event.key == K_F1:
                    self.light.switch_color()

        pressed = pygame.key.get_pressed()
        if pressed[K_UP]:
            self.distance -= 0.01 * dt
        if pressed[K_DOWN]:
            self.distance += 0.01 * dt
        if pressed[K_LEFT]:
            self.angle -= 0.005 * dt
        if pressed[K_RIGHT]:
            self.angle += 0.005 * dt

        self.distance = max(10, min(self.distance, 20))
        self.angle %= math.pi * 2

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    app = App()
    app.start()
