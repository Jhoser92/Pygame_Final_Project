import pygame
from pygame.locals import *
from pygame.sprite import spritecollide
from pygame.transform import scale
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

FPS = 60
fpsClock = pygame.time.Clock()

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# Define font.
font = pygame.font.SysFont('Berlin Sans FB Demi', 70)
font_score = pygame.font.SysFont('Berlin Sans FB Demi', 30)

# Define Game Variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 2
score = 0

# Define colors.
white = (255, 255, 255)
blue = (0, 0, 255)

# Load Images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
menu_img = pygame.image.load('img/menuscreen.png')
bdr1_img = pygame.image.load('img/bdr1.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

# Load Sounds (Credits in comment.)
pygame.mixer.music.load('sound/music.wav')             # Credit to Clinthammer(https://freesound.org/people/Clinthammer/sounds/179511/)
pygame.mixer.music.play(-1, 0.0, 5000)
rupee_fx = pygame.mixer.Sound('sound/rupee.wav')       # Credit to cabled_mess(https://freesound.org/people/cabled_mess/sounds/350874/)
rupee_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sound/jump.wav')         # Credit to se2001(https://freesound.org/people/se2001/sounds/518130/)
jump_fx.set_volume(0.5)
door_fx = pygame.mixer.Sound('sound/door.wav')         # Credit to Deela(https://freesound.org/people/Deela/sounds/487614/)
door_fx.set_volume(0.5)
gameover_fx = pygame.mixer.Sound('sound/gameover.wav') # Credit to ProjectsU012(https://freesound.org/people/ProjectsU012/sounds/333785/)
gameover_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# Function to reset level.
def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    spikes_group.empty()
    exit_group.empty()

    # Load in level data and create world.
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # Get mouse position.
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions.
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # Get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Handle animation.
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y  

            # Check for collision
            self.in_air = True
            for tile in world.tile_list:
                # Check for collision in x direction.
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Check for collision in y direction.
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below ground i.e jumping.
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Check if above ground i.e falling.
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
                
            # Check for collision with enemies.
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                gameover_fx.play()
            
            # Check for collision with spikes.
            if pygame.sprite.spritecollide(self, spikes_group, False):
                game_over = -1
                gameover_fx.play()

            # Check for collision with exit.
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
                door_fx.play()

            # Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('Game Over!', font, blue, (screen_width // 1.9) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # Draw player onto screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (40, 80))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

class World():
    def __init__(self, data):

        self.tile_list = []

        # Load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 6:
                    spikes = Spikes(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    spikes_group.add(spikes)
                if tile == 7:
                    rupee = Rupee(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    rupee_group.add(rupee)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 9:
                    img = pygame.transform.scale(bdr1_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1
    
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/enemy.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/spikes.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size //2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Rupee(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/rupee.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit_door.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
rupee_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Create dummy rupee for score.
score_rupee = Rupee(tile_size // 2, tile_size // 2)
rupee_group.add(score_rupee)

# Load in level data and create world.
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# Create buttons.
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 -350, screen_height // 2.5, start_img)
exit_button = Button(screen_width // 2 +100, screen_height // 2.5, exit_img)

# Main game loop.
run = True
while run == True:

    if main_menu == True:
        screen.blit(menu_img, (0, 0))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        screen.blit(bg_img, (0, 0))
        screen.blit(sun_img, (100, 100))
        world.draw()

        if game_over == 0:
            blob_group.update()
            # Update score.
            # Check is rupee has been collected.
            if pygame.sprite.spritecollide(player, rupee_group, True):
                score += 1
                rupee_fx.play()
            draw_text(' x ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        spikes_group.draw(screen)
        rupee_group.draw(screen)
        exit_group.draw(screen)
        
        game_over = player.update(game_over)

        # If player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
        
        # If player has completed the level.
        if game_over == 1:
            # Reset game and go to next level.
            level += 1
            if level <= max_levels:
                # Reset level.
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('You Win!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                # Restart game.
                if restart_button.draw():
                    level = 1
                    # Reset level.
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
    fpsClock.tick(FPS)

pygame.quit()