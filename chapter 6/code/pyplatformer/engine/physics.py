import pymunk

from .components import Component


__all__ = ['BoxCollider', 'SphereCollider', 'Physics', 'Rigidbody']


def coll_handler(_, arbiter):
    if len(arbiter.shapes) == 2:
        obj1 = arbiter.shapes[0].gameobject
        obj2 = arbiter.shapes[1].gameobject

        obj1.collide(obj2, arbiter.contacts)
        obj2.collide(obj1, arbiter.contacts)
    return True

space = pymunk.Space()
space.gravity = 0, -10
space.set_default_collision_handler(coll_handler)


class Rigidbody(Component):
    __slots__ = ['mass', 'is_static']

    def __init__(self, mass=1, is_static=True):
        self.mass = mass
        self.is_static = is_static

    def start(self):
        if not self.is_static:
            # Replace the static body
            pos = self.gameobject._body.position
            body = pymunk.Body(self.mass, 1666)
            body.position = pos
            self.gameobject._body = body

    def add_shape_to_space(self, shape):
        shape.collision_type = 1
        self.gameobject._shape = shape
        shape.gameobject = self.gameobject
        if self.is_static:
            space.add(shape)
        else:
            space.add(self.gameobject._body, shape)


class BoxCollider(Rigidbody):
    __slots__ = ['size']

    def __init__(self, width, height, mass=1, is_static=True):
        super(BoxCollider, self).__init__(mass, is_static)
        self.size = width, height

    def start(self):
        super(BoxCollider, self).start()
        body = self.gameobject._body
        shape = pymunk.Poly.create_box(body, self.size)
        self.add_shape_to_space(shape)


class SphereCollider(Rigidbody):
    __slots__ = ['radius']

    def __init__(self, radius, mass=1, is_static=True):
        super(SphereCollider, self).__init__(mass, is_static)
        self.radius = radius

    def start(self):
        super(SphereCollider, self).start()
        body = self.gameobject._body
        shape = pymunk.Circle(body, self.radius)
        self.add_shape_to_space(shape)


class Physics(object):
    @classmethod
    def step(cls, dt):
        space.step(dt)

    @classmethod
    def remove(cls, body):
        space.remove(body)
