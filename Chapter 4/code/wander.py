import math
import random
import cocos
import cocos.euclid as eu
import cocos.particle_systems as ps


def truncate(vector, m):
    magnitude = abs(vector)
    if magnitude > m:
        vector *= m / magnitude
    return vector


class Actor(cocos.cocosnode.CocosNode):
    def __init__(self, x, y):
        super(Actor, self).__init__()
        self.position = (x, y)
        self.velocity = eu.Vector2(0, 0)
        self.wander_angle = 0
        self.circle_distance = 50
        self.circle_radius = 10
        self.angle_change = math.pi / 4
        self.max_velocity = 50
        self.add(ps.Sun())
        self.schedule(self.update)

    def update(self, dt):
        circle_center = self.velocity.normalized() * \
                        self.circle_distance
        dx = math.cos(self.wander_angle)
        dy = math.sin(self.wander_angle)
        displacement = eu.Vector2(dx, dy) * self.circle_radius
        self.wander_angle += (random.random() - 0.5) * \
                             self.angle_change
        self.velocity += circle_center + displacement
        self.velocity = truncate(self.velocity, 
                                 self.max_velocity)
        self.position += self.velocity * dt
        self.position = (self.x % 640, self.y % 480)


class MainLayer(cocos.layer.Layer):
    def __init__(self):
        super(MainLayer, self).__init__()
        self.actor = Actor(320, 240)
        self.add(self.actor)


if __name__ == '__main__':
    cocos.director.director.init(caption='Steering Behaviors')
    scene = cocos.scene.Scene(MainLayer())
    cocos.director.director.run(scene)
