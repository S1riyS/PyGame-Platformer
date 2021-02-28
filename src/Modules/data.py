import pygame

# WINDOW
# WIDTH = 1280
# HEIGHT = 720

WIDTH = 1280
HEIGHT = 720

SURFACE_WIDTH = 512
SURFACE_HEIGHT = 288

MAP_WIDTH = 100
MAP_HEIGHT = 40

WINDOW_SIZE = WIDTH, HEIGHT
FPS = 75
CAPTION = 'Platformer'

# COLORS

# TILES
TILE_SIDE = 16

################ ПОВЕРХНОСТЬ ОТРИСОВКИ ################
display = pygame.Surface((SURFACE_WIDTH, SURFACE_HEIGHT))

################ ГРУППЫ СПРАЙТОВ ################
all_sprites = pygame.sprite.Group()
map_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

################ МАССИВЫ RECT`ов ################
tile_list = []
enemy_list = []

