import cocos.tiles
import cocos.actions as ac


RIGHT = ac.RotateBy(90, 1)
LEFT = ac.RotateBy(-90, 1)


def move(x, y):
    dur = abs(x+y) / 100.0
    return ac.MoveBy((x, y), duration=dur)


class Scenario(object):
    def __init__(self, tmx_map):
        self.tmx_map = tmx_map
        self.turret_slots = []
        self.bunker_position = None
        self.enemy_start = None
        self._actions = None

    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, actions):
        self._actions = ac.RotateBy(90, 0.5)
        for step in actions:
            self._actions += step

    def get_background(self):
        tmx_map = cocos.tiles.load('assets/tower_defense.tmx')
        bg = tmx_map[self.tmx_map]
        bg.set_view(0, 0, bg.px_width, bg.px_height)
        return bg


def get_scenario():
    sc = Scenario('map0')
    sc.actions = [move(610, 0), LEFT, move(0, 160),
                  LEFT, move(-415, 0), RIGHT,
                  move(0, 160), RIGHT, move(420, 0)]
    sc.enemy_start = (-80, 110)
    sc.bunker_position = (528, 430)
    sc.turret_slots = [(192, 352), (320, 352), (448, 352),
                       (192, 192), (320, 192), (448, 192),
                       (96, 32), (224, 32), (352, 32), (480, 32)]
    return sc
