from pygame.locals import *
from engine import *


class Platform(GameObject):
    def __init__(self, x, y, width, height):
        super(Platform, self).__init__(x, y)
        color = (0.2, 1, 0.5, 1)
        self.add_components(Cube(color, size=(width, height, 2)),
                            BoxCollider(width, height))


class Rotating(Component):
    speed = 50
    def update(self, dt):
        ax, ay, az = self.gameobject.rotation
        ay = (ay + self.speed * dt) % 360
        self.gameobject.rotation = ax, ay, az


class Pickup(GameObject):
    def __init__(self, x, y):
        super(Pickup, self).__init__(x, y)
        self.tag = 'pickup'
        color = (1, 1, 0.5, 1)
        self.add_components(Cube(color, size=(1, 1, 1)),
                            Rotating(), BoxCollider(1, 1))


class Disappear(Component):
    def update(self, dt):
        self.gameobject.velocity = 0, 0
        s1, s2, s3 = map(lambda s: s - dt*2, self.gameobject.scale)
        self.gameobject.scale = s1, s2, s3
        if s1 <= 0: self.gameobject.remove()


class Shoot(Component):
    def on_collide(self, other, contacts):
        self.gameobject.remove()


class Shooter(Component):
    __slots__ = ['ammo']

    def __init__(self):
        self.ammo = 0

    def update(self, dt):
        if Input.get_key_down(K_SPACE) and self.ammo > 0:
            self.ammo -= 1
            direction = 1 if self.gameobject.velocity.x > 0 else -1
            pos = self.gameobject.position
            shoot = GameObject(pos[0] + 1.5 * direction, pos[1])
            shoot.tag = 'shoot'
            shoot.add_components(Sphere(0.3, (1, 1, 0, 1)), Shoot(),
                                 SphereCollider(0.3, mass=0.1, is_static=False))
            shoot.apply_force(20 * direction, 0)

    def on_collide(self, other, contacts):
        if other.tag == 'pickup':
            self.ammo += 5
            other.add_component(Disappear())


class Shootable(Component):
    def on_collide(self, other, contacts):
        if other.tag == 'shoot':
            self.gameobject.add_component(Disappear())


class Enemy(GameObject):
    def __init__(self, x, y):
        super(Enemy, self).__init__(x, y)
        self.tag = 'enemy'
        color = (1, 0.2, 0.2, 1)
        self.add_components(Sphere(1, color), Shootable(),
                            SphereCollider(1, is_static=False))


class Respawn(Component):
    __slots__ = ['limit', 'spawn_position']

    def __init__(self, limit=-15):
        self.limit = limit
        self.spawn_position = None

    def start(self):
        self.spawn_position = self.gameobject.position

    def update(self, dt):
        if self.gameobject.position[1] < self.limit:
            self.respawn()

    def on_collide(self, other, contacts):
        if other.tag == 'enemy':
            self.respawn()

    def respawn(self):
        self.gameobject.velocity = 0, 0
        self.gameobject.position = self.spawn_position


class PlayerMovement(Component):
    __slots__ = ['can_jump']

    def __init__(self):
        self.can_jump = False

    def update(self, dt):
        d = Input.get_key(K_RIGHT) - Input.get_key(K_LEFT)
        self.gameobject.move(d * 5 * dt, 0)
        if Input.get_key(K_UP) and self.can_jump:
            self.can_jump = False
            self.gameobject.move(0, 8)

    def on_collide(self, other, contacts):
        self.can_jump = any(c.normal.y < 0 for c in contacts)


class Player(GameObject):
    def __init__(self, x, y):
        super(Player, self).__init__(x, y)
        self.add_components(Sphere(1, (1, 1, 1, 1)),
                            PlayerMovement(), Respawn(),
                            Shooter(), Camera(10, 20),
                            SphereCollider(1, is_static=False))


class PyPlatformer(Game):
    def __init__(self):
        super(PyPlatformer, self).__init__('PyPlatformer')
        self.player = Player(-2, 0)
        self.light = GameObject(0, 10, 0)
        self.light.add_component(Light(GL_LIGHT0))
        self.ground = [
            # Platform 1
            Platform(3, -2, 30, 1),
            Platform(-11, 3, 2, 9),
            Platform(8, 0, 2, 3),
            # Platform 2 & 3
            Platform(23, 0, 6, 1),
            Platform(40, 2, 24, 1),
            # Platform 4 & 5
            Platform(60, 3, 8, 1),
            Platform(84, 4, 26, 1)
        ]
        self.pickups = Pickup(60, 5)
        self.enemies = [Enemy(40, 4), Enemy(90, 6)]


if __name__ == '__main__':
    game = PyPlatformer()
    game.mainloop()
