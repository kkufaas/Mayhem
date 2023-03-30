""" This code is written by Kristina Kufaas and Hannah Vesetrud """
import cProfile
import random

import pygame
import math

pygame.init()
from config import *

screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
background = pygame.image.load(BACKGROUND)
background = pygame.transform.scale(background, (SCREEN_X, SCREEN_Y))
background.convert()
pygame.display.set_caption("MAYHEM")
font = pygame.sysfont.SysFont('Arial', 20)


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, image_path, pos_x, pos_y, control_keys, spaceship_group, player_number):
        super().__init__()
        self.bullet = None
        self.control_keys = control_keys
        """ Image properties """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.scaled_image = pygame.transform.scale(self.original_image, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
        self.image = self.scaled_image

        """ Rect and position properties """
        self.startPosition = (pos_x, pos_y)
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)

        """ Physics """
        self.thrust = 0.25
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.speed = SPEED

        """ Game scores """
        self.score = 0
        self.fuel = FUEL
        self.shoot = False
        self.bullet_callback = 0
        self.spaceship_number = player_number

        """ Group """
        self.spaceship_group = spaceship_group

    def move(self, keys):
        """ Provides the movement of the specified spaceship, as well as shooting and rotating """
        thrust_vector = pygame.math.Vector2()
        for key, direction in self.control_keys.items():
            if keys[key]:
                if direction == 'left':
                    self.angle += 3
                    self.rotate()
                elif direction == 'right':
                    self.angle -= 3
                    self.rotate()
                elif direction == 'up':
                    if self.fuel > 0:
                        thrust_vector += pygame.math.Vector2(self.thrust, -1).rotate(-self.angle)
                        self.fuel -= 1
                elif direction == 'shoot':
                    self.shoot = True
                    self.shooting()
        self.velocity += thrust_vector
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        if self.velocity.x > MAX_SPEED:
            self.velocity.x = 5
        elif self.velocity.x < -MAX_SPEED:
            self.velocity.x = -5
        if self.velocity.y > MAX_SPEED:
            self.velocity.y = 5
        elif self.velocity.y < -MAX_SPEED:
            self.velocity.y = -5

    """ Rotate function uses in 'move' when pressing left or right """

    def rotate(self):
        self.image = pygame.transform.rotate(self.scaled_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    """ If a spaceships is outside the screen boarders, they being returned to initial position and lose points """

    def screen_boarders(self):
        if self.rect.left > SCREEN_X or self.rect.right < 0 or self.rect.top > SCREEN_Y or self.rect.bottom < 0:
            self.reset_position()
            if self.spaceship_number == 1:
                spaceship1.score -= 1
            else:
                spaceship2.score -= 1

    """ Handles collisions """

    def collision(self):
        collisions_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for collision in collisions_platforms:
            if self.rect.bottom > collisions_platforms[0].rect.top and self.speed > 0:
                self.rect.bottom = collisions_platforms[0].rect.top
                self.fuel += 2
                if self.fuel > 100:
                    self.fuel = 100

        collisions_obstacles = pygame.sprite.spritecollide(self, obstacles, False)
        for collision in collisions_obstacles:
            self.reset_position()
            if self.spaceship_number == 1:
                spaceship1.score -= 1
            else:
                spaceship2.score -= 1

        collisions_ship = pygame.sprite.spritecollide(self, self.spaceship_group, False)
        for ship in collisions_ship:
            if ship != self:
                self.reset_position()
                ship.reset_position()
                spaceship1.score -= 1
                spaceship2.score -= 1

    def shooting(self):
        """ Calculates bullet track and returns bullet callback """
        # provides possibility to shoot again and again if there are no bullets on the screen
        if self.bullet_callback > 0:
            self.bullet_callback -= 1
        if self.shoot:
            if self.bullet_callback == 0:
                # Add a shift to the bullet's appear position
                shift_x = self.rect.centerx + math.cos(math.radians(self.angle))
                shift_y = self.rect.centery - math.sin(math.radians(self.angle))
                self.bullet = Bullet(shift_x, shift_y, self.angle + 90, RED, self.spaceship_group, self)
                all_sprites.add(self.bullet)
                self.bullet_callback = 10

    def gravity(self):
        """ Constant gravity """
        self.velocity.y += GRAVITY

    def platform_gravity(self):
        """ Drags spaceships onto platforms in initial appearing """
        self.velocity *= 0.99

    def reset_position(self):
        """ Puts spaceships in initial position after crashing """
        self.rect.center = self.startPosition
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.shoot = False
        self.image = pygame.transform.rotate(self.scaled_image, self.angle)
        self.spaceship_group.add(self)

    def score_ship1(self):
        """ Score display for spaceship 1 """
        spaceship1_score_position = (20, SCREEN_Y - 740)
        score = font.render("Score Spaceship 1: {}".format(self.score), False, GREEN)
        screen.blit(score, spaceship1_score_position)

    def score_ship2(self):
        """ Score display for spaceship 2 """
        spaceship2_score_position = (SCREEN_X - 220, SCREEN_Y - 740)
        score = font.render("Score Spaceship 2: {}".format(self.score), False, GREEN)
        screen.blit(score, spaceship2_score_position)

    def display_fuel1(self):
        """ Fuel display for spaceship 1 """
        fuel_position = (20, 20)
        fuel_score = font.render("Fuel Spaceship 1: {}".format(self.fuel), False, WHITE)
        screen.blit(fuel_score, fuel_position)

    def display_fuel2(self):
        """ Fuel display for spaceship 2 """
        fuel_position = (SCREEN_X - 220, 20)
        fuel_score = font.render("Fuel Spaceship 2: {}".format(self.fuel), False, WHITE)
        screen.blit(fuel_score, fuel_position)

    def update(self):
        """ Functions calling in all_sprites.update in main loop """
        self.gravity()
        self.platform_gravity()
        self.screen_boarders()
        self.collision()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, color, spaceship_group, shoots, radius=5, speed=10):
        super().__init__()
        self.image = pygame.Surface((radius * 2, radius * 2))
        """ Physics """
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.angle = angle
        self.pos_x = x
        self.pos_y = y
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.vel_y = -math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        """ Shooting """
        self.shoots = shoots
        self.spaceship_group = spaceship_group
        self.appear_time = pygame.time.get_ticks()
        self.collision = False

    def bullet_move(self):
        """ Calculates direction of a bullet """
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    def check_hit(self):
        """ Checks if any collision with a spaceship """
        if self.collision:
            ship_collisions = pygame.sprite.spritecollide(self, self.spaceship_group, False)
            for ship in ship_collisions:
                if ship != self.shoots:
                    ship.reset_position()
                    self.shoots.score += 1
                    return True
        return False

    def update(self):
        self.bullet_move()
        if pygame.time.get_ticks() - self.appear_time > 5:
            self.collision = True
        self.check_hit()


class Platform(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y, width):
        super().__init__()
        self.original_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (width, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image_path, pos_x, pos_y, height, width):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


""" Adding obstacle """
obstacles = pygame.sprite.Group()
for _ in range(4):
    obstacle = obstacles.add(Obstacle(os.path.join('src/assets', 'obstacle.png'), SCREEN_X / random.randint(2, 3),
                                      SCREEN_Y / random.randint(2, 4), OBSTACLE_HEIGHT,
                                      OBSTACLE_WIDTH))

""" Adding refill platforms """
platform1 = Platform(os.path.join('src/assets', 'platform.png'), SCREEN_X // 4, SCREEN_Y // 1.05,
                     SPACESHIP_WIDTH + 100)
platform2 = Platform(os.path.join('src/assets', 'platform.png'), SCREEN_X // 4 * 3, SCREEN_Y // 1.05,
                     SPACESHIP_WIDTH + 100)
platforms = pygame.sprite.Group()
platforms.add(platform1, platform2)

""" Adding spaceships """
spaceships = pygame.sprite.Group()
spaceship1 = Spaceship(os.path.join('src/assets', 'spaceship_1.png'), SCREEN_X // 4, SCREEN_Y // 2, {
    pygame.K_LEFT: 'left',
    pygame.K_RIGHT: 'right',
    pygame.K_UP: 'up',
    pygame.K_DOWN: 'shoot'}, spaceships, 1)

spaceship2 = Spaceship(os.path.join('src/assets', 'spaceship_2.png'), SCREEN_X // 4 * 3, SCREEN_Y // 2, {
    pygame.K_a: 'left',
    pygame.K_d: 'right',
    pygame.K_w: 'up',
    pygame.K_s: 'shoot'}, spaceships, 2)
spaceships.add(spaceship1, spaceship2)

""" Adding sprites """
all_sprites = pygame.sprite.Group()
all_sprites.add([*obstacles], [*platforms], [*spaceships])


def main():
    clock = pygame.time.Clock()
    game = True
    while game:
        screen.blit(background, (0, 0))
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
        keys_pressed = pygame.key.get_pressed()
        for ship in spaceships:
            ship.move(keys_pressed)
        spaceship1.score_ship1()
        spaceship2.score_ship2()
        spaceship1.display_fuel1()
        spaceship2.display_fuel2()
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    cProfile.run('main()')
