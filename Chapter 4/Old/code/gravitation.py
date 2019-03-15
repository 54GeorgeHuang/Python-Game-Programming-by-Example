import math

from cocos.cocosnode import CocosNode
from cocos.director import director

import cocos.layer
import cocos.scene
import cocos.euclid as eu
import cocos.collision_model as cm
import cocos.particle_systems as ps

from pyglet.window import key


class ActorExplosion(ps.ParticleSystem):
    total_particles = 400
    duration = 0.1
    gravity = eu.Point2(0, 0)
    angle = 90.0
    angle_var = 360.0
    speed = 40.0
    speed_var = 20.0
    life = 3.0
    life_var = 1.5
    emission_rate = total_particles / duration
    start_color_var = ps.Color(0.0, 0.0, 0.0, 0.2)
    end_color = ps.Color(0.0, 0.0, 0.0, 1.0)
    end_color_var = ps.Color(0.0, 0.0, 0.0, 0.0)
    size = 15.0
    size_var = 10.0
    blend_additive = True

    def __init__(self, pos, color):
        super(ActorExplosion, self).__init__()
        self.position = pos
        self.start_color = color


def truncate(vector, m):
    magnitude = abs(vector)
    if magnitude > m:
        vector *= m / magnitude
    return vector


class Actor(CocosNode):
    def __init__(self, x, y, r):
        super(Actor, self).__init__()
        self.position = (x, y)
        self._cshape = cm.CircleShape(self.position, r)

    @property
    def cshape(self):
        self._cshape.center = eu.Vector2(self.x, self.y)
        return self._cshape


class MovingActor(Actor):
    def __init__(self, x, y, r):
        super(MovingActor, self).__init__(x, y, r)
        self._planet = None
        self._distance = 0
        self.angle = 0
        self.rotationSpeed = 0.6
        self.schedule(self.update)

    @property
    def planet(self):
        return self._planet

    @planet.setter
    def planet(self, val):
        if val is not None:
            dx, dy = self.x - val.x, self.y - val.y
            self.angle = -math.atan2(dy, dx)
            self._distance = abs(eu.Vector2(dx, dy))
        self._planet = val

    def update(self, dt):
        if self.planet is None:
            return
        dist = self._distance
        self.angle = (self.angle + self.rotationSpeed * dt) % (math.pi * 2)
        self.x = self.planet.x + dist * math.cos(self.angle)
        self.y = self.planet.y - dist * math.sin(self.angle)


class Planet(Actor):
    instances = []

    def __init__(self, x, y, r=50):
        super(Planet, self).__init__(x, y, r)
        particles = ps.Sun()
        particles.start_color = ps.Color(0.5, 0.5, 0.5, 1.0)
        particles.size = r * 2
        self.add(particles)
        self.instances.append(self)


class Player(MovingActor):
    def __init__(self, x, y, planet):
        super(Player, self).__init__(x, y, 16)
        self.planet = planet
        self.rotationSpeed = 1
        self.linearSpeed = 80
        self.direction = eu.Vector2(0, 0)
        self.particles = ps.Meteor()
        self.particles.size = 50
        self.add(self.particles)

    def update(self, dt):
        if self.planet is not None:
            super(Player, self).update(dt)
            gx = 20 * math.cos(self.angle)
            gy = 20 * math.sin(self.angle)
            self.particles.gravity = eu.Point2(gx, -gy)
        else:
            self.position += self.direction * dt

    def switch(self):
        new_dir = eu.Vector2(self.y - self.planet.y,
                             self.planet.x - self.x)
        self.direction = new_dir.normalized() * self.linearSpeed
        self.planet = None
        self.particles.gravity = eu.Point2(-self.direction.x, -self.direction.y)


class PickupParticles(ps.Sun):
    size = 20
    start_color = ps.Color(0.7, 0.7, 0.2, 1.0)


class Pickup(MovingActor):
    def __init__(self, x, y, planet):
        super(Pickup, self).__init__(x, y, 10)
        self.planet = planet
        self.gravity_factor = 50
        self.particles = PickupParticles()
        self.add(self.particles)


class Enemy(Actor):
    def __init__(self, x, y, target):
        super(Enemy, self).__init__(x, y, 40)
        self.velocity = eu.Vector2(0, 0)
        self.speed = 2
        self.max_force = 5
        self.max_velocity = 30
        self.max_ahead = 300
        self.max_avoid_force = 500
        self.target = target
        self.add(ps.Sun())
        self.schedule(self.update)

    def update(self, dt):
        if self.target is None:
            return
        distance = self.target.position - eu.Vector2(self.x, self.y)
        steering = distance * self.speed - self.velocity
        steering += self.avoid_force()
        steering = truncate(steering, self.max_force)
        self.velocity = truncate(self.velocity + steering,
                                 self.max_velocity)
        self.position += self.velocity * dt

    def avoid_force(self):
        avoid = eu.Vector2(0, 0)
        ahead = self.velocity * self.max_ahead / self.max_velocity
        l = ahead.dot(ahead)
        if l == 0:
            return avoid
        closest, closest_dist = None, None
        for obj in Planet.instances:
            w = eu.Vector2(obj.x - self.x, obj.y - self.y)
            t = ahead.dot(w)
            if 0 < t < l:
                proj = self.position + ahead * t / l
                dist = abs(obj.position - proj)
                if dist < obj.cshape.r and \
                   (closest is None or dist < closest_dist):
                    closest, closest_dist = obj.position, dist
        if closest is not None:
            avoid = self.position + ahead - closest
            avoid = avoid.normalized() * self.max_avoid_force
        return avoid


class GameLayer(cocos.layer.Layer):
    def __init__(self):
        super(GameLayer, self).__init__()
        x, y = director.get_window_size()
        cell_size = 32
        self.coll_man = cm.CollisionManagerGrid(0, x, 0, y, cell_size, cell_size)
        self.planet_area = 400
        planet1 = self.add_planet(450, 280)
        planet2 = self.add_planet(180, 200)
        planet3 = self.add_planet(270, 440)
        planet4 = self.add_planet(650, 480)
        planet5 = self.add_planet(700, 150)
        self.add_pickup(250, 250, planet2)
        self.add_pickup(740, 480, planet4)
        self.add_pickup(700, 60, planet5)
        self.player = Player(300, 350, planet3)
        self.add(self.player)
        self.add(Enemy(600, 100, self.player))
        self.schedule(self.game_loop)

    def add_pickup(self, x, y, target):
        pickup = Pickup(x, y, target)
        self.add(pickup)

    def add_planet(self, x, y):
        planet = Planet(x, y)
        self.add(planet)
        return planet

    def game_loop(self, _):
        self.coll_man.clear()
        for node in self.get_children():
            if isinstance(node, Actor):
                self.coll_man.add(node)
        if self.player.is_running:
            self.process_player_collisions()

    def process_player_collisions(self):
        player = self.player
        for obj in self.coll_man.iter_colliding(player):
            if isinstance(obj, Pickup):
                self.add(ActorExplosion(obj.position,
                                    obj.particles.start_color))
                obj.kill()
            else:
                self.add(ActorExplosion(player.position, player.particles.start_color))
                player.kill()

    is_event_handler = True

    def on_key_press(self, k, _):
        if k != key.SPACE:
            return
        if self.player.planet is None:
            self.player.planet = self.find_closest_planet()
        else:
            self.player.switch()

    def find_closest_planet(self):
        ranked = self.coll_man.ranked_objs_near(self.player, self.planet_area)
        planet = next(filter(lambda x: isinstance(x[0], Planet),
                             ranked))
        return planet[0] if planet is not None else None


if __name__ == '__main__':
    director.init(width=850, height=600, caption='Gravitation')
    director.run(cocos.scene.Scene(GameLayer()))
