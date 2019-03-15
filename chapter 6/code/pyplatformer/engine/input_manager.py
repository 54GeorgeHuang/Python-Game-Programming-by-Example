from collections import defaultdict
import pygame

class Input(object):
    quit_flag = False
    keys = defaultdict(bool)
    keys_down = defaultdict(bool)

    @classmethod
    def update(cls):
        cls.keys_down.clear()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cls.quit_flag = True
            if event.type == pygame.KEYUP:
                cls.keys[event.key] = False
            if event.type == pygame.KEYDOWN:
                cls.keys[event.key] = True
                cls.keys_down[event.key] = True

    @classmethod
    def get_key(cls, key):
        return cls.keys[key]

    @classmethod
    def get_key_down(cls, key):
        return cls.keys_down[key]
