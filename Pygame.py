import pygame
from pygame import image
from pygame import rect
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
pause_fnt = pygame.font.SysFont('Berlin Sans FB Demi', 90)
go_fnt = pygame.font.SysFont('Berlin Sans FB Demi', 90)
font_score = pygame.font.SysFont('Berlin Sans FB Demi', 30)

# Define Game Variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 10
score = 0
exit_score = 5


# Define colors.
white = (255, 255, 255)
blue = (0, 0, 255)

# Load Images
sun_img = pygame.image.load('img/world1/sun.png')
moon_img = pygame.image.load('img/world2/moon.png')
bg_img = pygame.image.load('img/world1/sky.png')
menu_img = pygame.image.load('img/menuscreen.png')
bdr1_img = pygame.image.load('img/bdr1.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
exit2_img = pygame.image.load('img/exit_btn2.png')

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

# Function for pause
def pause():
    paused = True

    # Notify the user what to do when paused.
    draw_text('-Paused-', pause_fnt, blue, (screen_width // 2.2) - 140, screen_height // 4)
    draw_text('P to continue', font, blue, (screen_width // 2.3) - 140, screen_height // 2.5)
    draw_text('Q to quit', font, blue, (screen_width // 2.3) - 140, screen_height // 2)
    pygame.display.update()  # Update surface.

    while paused:
        # Quit event.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Event to handle key presses when paused.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        
        fpsClock.tick(FPS)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# Function to reset level.
def reset_level(level):
    player.reset(50, screen_height - 130)
    blob_group.empty()
    platform_group.empty()
    spikes_group.empty()
    exit_group.empty()
    rupee_group.empty()

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
        col_thresh = 20

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
            if self.in_air == True and self.jumped == True:
                self.image = self.jump_image
                if self.direction == 1:
                    self.image = self.jump_image
                if self.direction == -1:
                    self.image = self.jump_left_image
            elif self.in_air == False and self.jumped == False:
                self.image = self.images_right[self.index]
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
            if score >= exit_score:
                if pygame.sprite.spritecollide(self, exit_group, False):
                    game_over = 1
                    door_fx.play()
            
            # Check for collision with edges.
            if self.rect.x >= screen_width or self.rect.x < 0 or self.rect.y >= screen_height or self.rect.y < 0:
                game_over = -1
                gameover_fx.play()

            # Check for collision with platforms.
            for platform in platform_group:
                # Collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Collision in the x direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below platform.
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # Check if above platform
                    elif abs ((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # Move sideways with platform.
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('Game Over!', go_fnt, blue, (screen_width // 2.4) - 140, screen_height // 3)
            if self.rect.y > 200:
                self.rect.y -= 5

        # Draw player onto screen
        screen.blit(self.image, self.rect)
       

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
        self.jump_image = pygame.image.load('img/guyjump.png')
        self.jump_image = pygame.transform.scale(self.jump_image, (40, 80))
        self.jump_left_image = pygame.transform.flip(self.jump_image, True, False)
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
        dirt_img = pygame.image.load('img/world1/dirt.png')
        grass_img = pygame.image.load('img/world1/grass.png')
        if level > 5 and level < 11:
            grass_img = pygame.image.load('img/world2/grass2.png')
            dirt_img = pygame.image.load('img/world2/dirt2.png')
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
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
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
            

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/world1/enemy.png')
        if level > 5 and level < 11:
            self.image = pygame.image.load('img/world2/enemy2.png')
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

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/world1/platform.png')
        if level > 5 and level < 11:
            img = pygame.image.load('img/world2/platform2.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y


    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/world1/spikes.png')
        if level > 5 and level < 11:
            img = pygame.image.load('img/world2/thorns.png')
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


player = Player(50, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
rupee_group = pygame.sprite.Group()
rupeescore_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Create dummy rupee for score.
score_rupee = Rupee(tile_size // 2, tile_size // 2)
rupeescore_group.add(score_rupee)

# Load in level data and create world.
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# Create buttons.
restart_button = Button(screen_width // 2 - 60, screen_height // 2, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2.5, start_img)
exit_button = Button(screen_width // 2 + 100, screen_height // 2.5, exit_img)
exit2_button = Button(screen_width // 2 - 40, screen_height // 1.8, exit2_img)

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
        if level <= 5:
            screen.blit(sun_img, (100, 100))
        elif level > 5 and level < 11:
            screen.blit(moon_img, (100, 100))
        if level == 1:
            draw_text('Collect all 5 rupees', font, blue, (screen_width // 3) - 140, screen_height // 3)
            draw_text('to exit!', font, blue, (screen_width // 2) - 140, screen_height // 2.5)
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()
            # Update score.
            # Check is rupee has been collected.
            if pygame.sprite.spritecollide(player, rupee_group, True):
                score += 1
                rupee_fx.play()
            draw_text(' x ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        spikes_group.draw(screen)
        rupee_group.draw(screen)
        rupeescore_group.draw(screen)
        exit_group.draw(screen)
        
        game_over = player.update(game_over)

        # If player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
                exit_score = 5
        
        # If player has completed the level.
        if game_over == 1:
            # Reset game and go to next level.
            level += 1
            exit_score += 5
            if level > 5 and level < 11:
                bg_img = pygame.image.load('img/world2/forest.png')
            if level <= max_levels:
                # Reset level.
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('You Win!', go_fnt, blue, (screen_width // 2.2) - 140, screen_height // 3)
                # Restart game.
                if restart_button.draw():
                    level = 1
                    # Reset level.
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                    exit_score = 5
                    if level == 1:
                        bg_img = pygame.image.load('img/world1/sky.png')
                if exit2_button.draw():
                    run = False

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if main_menu == False:
            key = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if key[pygame.K_p]:
                    pause()

    pygame.display.update()
    fpsClock.tick(FPS)

pygame.quit()