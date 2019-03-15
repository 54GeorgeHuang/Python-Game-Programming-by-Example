import sys

import pygame

import pymunk as pm

from OpenGL.GL import *
from OpenGL.GLU import *

from .components import *
from .input_manager import Input
from .physics import BoxCollider, SphereCollider, Physics, Rigidbody


class GameObject(object):
    instances = []
    
    def __init__(self, x=0, y=0, z=0, scale=(1, 1, 1)):
        self._body = pm.Body()
        self._body.position = x, y
        self._shape = None
        self._ax = 0
        self._ay = 0
        self._z = z
        self.tag = ''
        self.scale = scale
        self.components = []
        GameObject.instances.append(self)

    @property
    def position(self):
        pos = self._body.position
        return pos.x, pos.y, self._z

    @position.setter
    def position(self, pos):
        self._body.position = pos[0], pos[1]
        self._z = pos[2]

    @property
    def rotation(self):
        return self._ax, self._ay, self._body.angle

    @rotation.setter
    def rotation(self, rot):
        self._ax = rot[0]
        self._ay = rot[1]
        self._body.angle = rot[2]

    @property
    def velocity(self):
        return self._body.velocity

    @velocity.setter
    def velocity(self, vel):
        self._body.velocity = vel

    def move(self, x, y):
        self._body.apply_impulse((x, y))

    def apply_force(self, x, y):
        self._body.apply_force((x, y))

    def add_components(self, *components):
        for component in components:
            self.add_component(component)

    def add_component(self, component):
        self.components.append(component)
        component.gameobject = self
        component.start()

    def get_component_by_type(self, cls):
        for component in self.components:
            if isinstance(component, cls):
                return component

    def remove_component(self, component):
        component.stop()
        self.components.remove(component)

    def render(self):
        for component in self.components:
            if isinstance(component, Renderable):
                component.render()

    def update(self, dt):
        for component in self.components:
            component.update(dt)

    def remove(self):
        for component in self.components:
            self.remove_component(component)
        if self._shape is not None:
            Physics.remove(self._shape)
        GameObject.instances.remove(self)

    def collide(self, other, contacts):
        for component in self.components:
            component.on_collide(other, contacts)


class Game(object):
    def __init__(self, caption, width=800, height=600):
        self.caption = caption
        self.width = width
        self.height = height
        self.fps = 60
        self.screen = None

    def mainloop(self):
        self.setup()
        clock = pygame.time.Clock()
        while not Input.quit_flag:
            dt = clock.tick(self.fps)
            dt /= 1000
            Physics.step(dt)
            self.update(dt)
            self.render()
        pygame.quit()
        sys.exit()

    def setup(self):
        pygame.init()
        size = self.width, self.height
        self.screen = pygame.display.set_mode(size,
                                              pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption(self.caption)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.7, 1, 1)
        glMatrixMode(GL_PROJECTION)
        aspect = self.width / self.height
        gluPerspective(45, aspect, 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def update(self, dt):
        Input.update()
        for gameobject in GameObject.instances:
            gameobject.update(dt)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if Camera.instance is not None:
            Camera.instance.render()
        for gameobject in GameObject.instances:
            gameobject.render()
        pygame.display.flip()
