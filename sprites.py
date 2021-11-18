# Sprite classes for platform game
import pygame as pg
from settings import *
vec = pg.math.Vector2

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width * 2, height * 2))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game, sprites):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.sprites = sprites
        self.image = sprites[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (15, HEIGHT / 2)
        self.pos = vec(15, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.rot = 0
        self.current_image = self.image
        self.last_update = 0

        self.frame_number = 0
        self.last_update_animation = 0

    def jump(self):
        # only jump not near top
        if self.rect.top > GAP_BUFFER:
            self.vel.y = -PLAYER_JUMP

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update_animation > 100:
            self.last_update_animation = now
            self.current_image = self.sprites[self.frame_number % 4]
            self.current_image.set_colorkey(BLACK)
            self.frame_number += 1

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = max(self.vel.y * -3, -90)
            new_image = pg.transform.rotate(self.current_image, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.acc = vec(PLAYER_ACC, PLAYER_GRAV)

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

class Platform(pg.sprite.Sprite):
    scored = False

    def __init__(self, x, y, img):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
