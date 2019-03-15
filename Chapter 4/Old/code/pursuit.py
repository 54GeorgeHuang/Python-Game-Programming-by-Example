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
        self.add(ps.Sun())
        self.schedule(self.update)

    def update(self, dt):
        if self.target is None:
            return
        future_pos = self.target.position + self.target.velocity
        distance = future_pos - eu.Vector2(self.x, self.y)
        steering = distance * self.speed - self.velocity
        steering = truncate(steering, self.max_force)
        self.velocity = truncate(self.velocity + steering, 
                                 self.max_velocity)
        self.position += self.velocity * dt


class MainLayer(cocos.layer.Layer):
    def __init__(self):
        super(MainLayer, self).__init__()
        self.target = ps.Sun()
        self.target.position = (40, 40)
        self.target.start_color = ps.Color(0.2, 0.7, 0.7, 1.0)
        self.target.velocity = eu.Vector2(50, 0)
        self.add(self.target)
        self.actor = Actor(320, 240)
        self.actor.target = self.target
        self.add(self.actor)
        self.schedule(self.update)

    def update(self, dt):
        self.target.position += self.target.velocity * dt


if __name__ == '__main__':
    cocos.director.director.init(caption='Steering Behaviors')
    scene = cocos.scene.Scene(MainLayer())
    cocos.director.director.run(scene)
