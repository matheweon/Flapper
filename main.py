# KidsCanCode - Game Development with Pygame video series
# Jumpy! (a platform game) - Part 6
# Video link: https://youtu.be/BKtiVKNsOYk
# Game Over (and score)

import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

        self.bird_high_wing = self.spritesheet.get_image(3, 491, 18, 13)
        self.bird_mid_wing = self.spritesheet.get_image(31, 491, 18, 13)
        self.bird_low_wing = self.spritesheet.get_image(59, 491, 18, 13)
        self.top_pipe = self.spritesheet.get_image(56, 323, 27, 161)
        self.bottom_pipe = self.spritesheet.get_image(85, 323, 27, 161)

        self.floor = Platform(*FLOOR_POS, pg.Surface(FLOOR_DIMS))
        self.floor.image.fill(GREEN)

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self, [self.bird_high_wing, self.bird_mid_wing, self.bird_low_wing, self.bird_mid_wing])
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.floor)
        self.platforms.add(self.floor)
        for plat in PLATFORM_LIST:
            x, y = plat
            p_top = Platform(x, y - PIPE_HEIGHT, self.top_pipe)
            p_bot = Platform(x, y + VERTICAL_GAP, self.bottom_pipe)
            self.all_sprites.add(p_top)
            self.all_sprites.add(p_bot)
            self.platforms.add(p_top)
            self.platforms.add(p_bot)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

        # if player reaches right half of the screen
        if self.player.rect.right >= WIDTH / 2:
            self.player.pos.x -= abs(self.player.vel.x)
            for p in self.platforms:
                # move every platform except for the floor
                if not p == self.platforms.sprites()[0]:
                    p.rect.right -= abs(self.player.vel.x)
                    # add to score when player passes
                    if p.rect.right < self.player.rect.left and p.scored == False:
                        self.score += 0.5
                        p.scored = True
                    # kill when off screen
                    if p.rect.right <= 0:
                        p.kill()

        # spawn pipe when pipe leaves the screen
        while len(self.platforms) < 7:
            gap = random.randrange(GAP_BUFFER, HEIGHT - VERTICAL_GAP - GAP_BUFFER - 40)
            #top_pipe = Platform(X_SPAWN, 0, PIPE_WIDTH, gap)
            #bot_pipe = Platform(X_SPAWN, gap + VERTICAL_GAP, PIPE_WIDTH, HEIGHT - gap - VERTICAL_GAP)
            top_pipe = Platform(1140, gap - PIPE_HEIGHT, self.top_pipe)
            bot_pipe = Platform(1140, gap + VERTICAL_GAP, self.bottom_pipe)

            self.platforms.add(top_pipe)
            self.platforms.add(bot_pipe)
            self.all_sprites.add(top_pipe)
            self.all_sprites.add(bot_pipe)

        # die on platform collision
        hits = pg.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            self.all_sprites.empty()
            self.playing = False

        self.player.animate()
        self.player.rotate()

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(int(self.score)), 22, WHITE, WIDTH / 2, 15)
        self.screen.blit(self.floor.image, FLOOR_POS)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Space to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.score = int(self.score)
        # game over/continue
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
