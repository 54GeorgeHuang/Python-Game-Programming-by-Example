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
        self.speed = 2
        self.max_force = 5
        self.max_velocity = 200
        self.target = None
        self.seek = True
        self.add(ps.Sun())
        self.schedule(self.update)

    def update(self, dt):
        if self.target is None:
            return
        distance = self.target - eu.Vector2(self.x, self.y)
        steering = distance * self.speed - self.velocity
        steering = truncate(steering, self.max_force)
        self.velocity = truncate(self.velocity + steering, 
                                 self.max_velocity)
        direction = 1 if self.seek else -1
        self.position += self.velocity * dt * direction


class MainLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(MainLayer, self).__init__()
        self.actor = Actor(320, 240)
        self.add(self.actor)

    def on_mouse_motion(self, x, y, dx, dy):
        self.actor.target = eu.Vector2(x, y)

    def on_mouse_press(self, x, y, buttons, mod):
        self.actor.seek = not self.actor.seek


if __name__ == '__main__':
    cocos.director.director.init(caption='Steering Behaviors')
    scene = cocos.scene.Scene(MainLayer())
    cocos.director.director.run(scene)
