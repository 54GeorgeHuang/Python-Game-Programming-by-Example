import math

import cocos.sprite
import cocos.audio
import cocos.actions as ac
import cocos.euclid as eu
import cocos.collision_model as cm

import pyglet.image
from pyglet.image import Animation

raw = pyglet.image.load('assets/explosion.png')
seq = pyglet.image.ImageGrid(raw, 1, 8)
explosion_img = Animation.from_image_sequence(seq, 0.07, False)


class Explosion(cocos.sprite.Sprite):
    def __init__(self, pos):
        super(Explosion, self).__init__(explosion_img, pos)
        self.do(ac.Delay(1) + ac.CallFunc(self.kill))


class Shoot(cocos.sprite.Sprite):
    def __init__(self, pos, offset, target):
        super(Shoot, self).__init__('shoot.png', position=pos)
        self.do(ac.MoveBy(offset, 0.1) +
                ac.CallFunc(self.kill) +
                ac.CallFunc(target.hit))


class Hit(ac.IntervalAction):
    def init(self, duration=0.5):
        self.duration = duration

    def update(self, t):
        self.target.color = (255, 255 * t, 255 * t)


class TurretSlot(object):
    def __init__(self, pos, side):
        self.cshape = cm.AARectShape(eu.Vector2(*pos), side*0.5, side*0.5)


class Actor(cocos.sprite.Sprite):
    def __init__(self, img, x, y):
        super(Actor, self).__init__(img, position=(x, y))
        self._cshape = cm.CircleShape(self.position,
                                      self.width * 0.5)

    @property
    def cshape(self):
        self._cshape.center = eu.Vector2(self.x, self.y)
        return self._cshape


class Turret(Actor):
    def __init__(self, x, y):
        super(Turret, self).__init__('turret.png', x, y)
        self.add(cocos.sprite.Sprite('range.png', opacity=50, scale=5))
        self.cshape.r = 125.0
        self.target = None
        self.period = 2.0
        self.reload = 0.0
        self.schedule(self._shoot)

    def _shoot(self, dt):
        if self.reload < self.period:
            self.reload += dt
        elif self.target is not None:
            self.reload -= self.period
            offset = eu.Vector2(self.target.x - self.x,
                                self.target.y - self.y)
            pos = self.cshape.center + offset.normalized() * 20
            self.parent.add(Shoot(pos, offset, self.target))

    def collide(self, other):
        self.target = other
        if self.target is not None:
            x, y = other.x - self.x, other.y - self.y
            angle = -math.atan2(y, x)
            self.rotation = math.degrees(angle)


class Enemy(Actor):
    def __init__(self, x, y, actions):
        super(Enemy, self).__init__('tank.png', x, y)
        self.health = 100
        self.score = 20
        self.destroyed = False
        self.do(actions)

    def hit(self):
        self.health -= 25
        self.do(Hit())
        if self.health <= 0 and self.is_running:
            self.destroyed = True
            self.explode()

    def explode(self):
        self.parent.add(Explosion(self.position))
        self.kill()


class Bunker(Actor):
    def __init__(self, x, y):
        super(Bunker, self).__init__('bunker.png', x, y)
        self.hp = 100

    def collide(self, other):
        if isinstance(other, Enemy):
            self.hp -= 10
            other.explode()
        if self.hp <= 0:
            self.kill()
