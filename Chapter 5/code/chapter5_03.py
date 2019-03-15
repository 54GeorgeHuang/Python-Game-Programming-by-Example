import sys
import pygame
from pygame.locals import *

class App(object):
    def __init__(self, width=400, height=300):
        self.title = 'Hello, Pygame!'
        self.fps = 100
        self.width = width
        self.height = height
        self.circle_pos = width/2, height/2
        
    def start(self):
        pygame.init()
        size = (self.width, self.height)
        screen = pygame.display.set_mode(size, DOUBLEBUF)
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pressed = pygame.key.get_pressed()
            x, y = self.circle_pos
            if pressed[K_UP]:
                y -= 0.5 * dt
            if pressed[K_DOWN]:
                y += 0.5 * dt
            if pressed[K_LEFT]:
                x -= 0.5 * dt
            if pressed[K_RIGHT]:
                x += 0.5 * dt
            self.circle_pos = x, y
            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, (0, 250, 100),
                               (int(x), int(y)), 30)
            pygame.display.flip()

if __name__ == '__main__':
    app = App()
    app.start()
