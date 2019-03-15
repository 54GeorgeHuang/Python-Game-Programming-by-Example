import cocos.director
import cocos.scene
import cocos.sprite
import cocos.layer
import cocos.actions as ac


class Hit(ac.IntervalAction):
    def init(self, duration=0.5):
        self.duration = duration

    def update(self, t):
        self.target.color = (255, 255 * t, 255 * t)


if __name__ == '__main__':
    cocos.director.director.init(caption='Actions 101')

    layer = cocos.layer.Layer()
    sprite = cocos.sprite.Sprite('tank.png', position=(200, 200))
    sprite.do(ac.MoveBy((100, 0), 3) + Hit() + ac.MoveBy((50, 0), 2))
    layer.add(sprite)
    
    scene = cocos.scene.Scene(layer)
    cocos.director.director.run(scene)
