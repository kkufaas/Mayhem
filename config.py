import pygame
import os

# Screen properties
SCREEN_X = 1200
SCREEN_Y = 800

# colors and pics
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (124, 252, 0)
BACKGROUND = os.path.join('src/assets', 'space.png')

# dimensions
SPACESHIP_WIDTH = 80
SPACESHIP_HEIGHT = 40
BULLET_WIDTH = 30
BULLET_HEIGHT = 30
OBSTACLE_WIDTH = 70
OBSTACLE_HEIGHT = 70

FUEL = 100
FONT = pygame.sysfont.SysFont('Arial', 30)
CONTROL_SET1 = []

# Physics:
MAX_SPEED = 5
SPEED = 3
FPS = 50
GRAVITY = 0.05