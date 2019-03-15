import cocos
from cocos.menu import *
import pyglet.app

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Sample menu')
        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        self.difficulty = ['Easy', 'Normal', 'Hard']
        m1 = MenuItem('New Game', self.start_game)
        m2 = EntryMenuItem('Player name:', self.set_player_name,
                           'John Doe', max_length=10)
        m3 = MultipleMenuItem('Difficuly: ', self.set_difficulty,
                              self.difficulty)
        m4 = ToggleMenuItem('Show FPS: ', self.show_fps, False)
        m5 = MenuItem('Quit', pyglet.app.exit)
        self.create_menu([m1, m2, m3, m4, m5],
                         shake(), shake_back())

    def start_game(self):
        print('Starting a new game!')

    def set_player_name(self, name):
        print('Player name:', name)

    def set_difficulty(self, index):
        print('Difficulty set to', self.difficulty[index])

    def show_fps(self, val):
        cocos.director.director.show_FPS = val

if __name__ == '__main__':
    cocos.director.director.init(caption='Sample app', width=800)
    scene = cocos.scene.Scene(MainMenu())
    cocos.director.director.run(scene)
