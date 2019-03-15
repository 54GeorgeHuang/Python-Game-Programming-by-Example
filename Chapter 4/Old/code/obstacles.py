import cocos
import cocos.euclid as eu
import cocos.particle_systems as ps


def truncate(vector, m):
    magnitude = abs(vector)
    if magnitude > m:
        vector *= m / magnitude
    return vector


class Obstacle(cocos.cocosnode.CocosNode):
    instances = []
    
    def __init__(self, x, y, r):
        super(Obstacle, self).__init__()
        self.position = (x, y)
        self.radius = r
        particles = ps.Sun()
        particles.size = r * 2
        particles.start_color = ps.Color(0.0, 0.7, 0.0, 1.0)
        self.add(particles)
        self.instances.append(self)


class Actor(cocos.cocosnode.CocosNode):
    def __init__(self, x, y):
        super(Actor, self).__init__()
        self.position = (x, y)
        self.velocity = eu.Vector2(0, 0)
        self.speed = 2
        self.max_velocity = 300
        self.max_force = 10
        self.target = None
        self.max_ahead = 200
        self.max_avoid_force = 300
        self.add(ps.Sun())
        self.schedule(self.update)

    def update(self, dt):
        if self.target is None:
            return
        distance = self.target - eu.Vector2(self.x, self.y)
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
        for obj in Obstacle.instances:
            w = eu.Vector2(obj.x - self.x, obj.y - self.y)
            t = ahead.dot(w)
            if 0 < t < l:
                proj = self.position + ahead * t / l
                dist = abs(obj.position - proj)
                if dist < obj.radius and \
                   (closest is None or dist < closest_dist):
                    closest, closest_dist = obj.position, dist
        if closest is not None:
            avoid = self.position + ahead - closest
            avoid = avoid.normalized() * self.max_avoid_force
        return avoid


class MainLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(MainLayer, self).__init__()
        self.add(Obstacle(200, 200, 40))
        self.add(Obstacle(240, 350, 50))
        self.add(Obstacle(500, 300, 50))
        self.actor = Actor(320, 240)
        self.add(self.actor)

    def on_mouse_motion(self, x, y, dx, dy):
        self.actor.target = eu.Vector2(x, y)


if __name__ == '__main__':
    cocos.director.director.init(caption='Steering Behaviors')
    scene = cocos.scene.Scene(MainLayer())
    cocos.director.director.run(scene)
