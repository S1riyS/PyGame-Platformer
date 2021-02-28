################ ИМПОРТ МОДУЛЕЙ ################
import pygame
from pygame.locals import *
from pygame.math import Vector2
import json
import time
from math import sqrt, atan2, cos, sin, hypot
from PIL import Image
import numpy as np


from Modules.data import *
from Modules.camera import *
# from Modules.shooting import *
# from Modules.map import *
# from Modules.functions import load_tiles
# from Modules.player import *
# from Modules.enemy import *

# from Modules.game import Game

# game = Game()
# game.start()

################ НАСТРОЙКИ ОКНА ################
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

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
player_list = []

################ ТЕСТ НА КОЛЛИЗИЮ ################
def collision_test(rect, tiles_list:list):
    """Вторым значением фунция принимает список pygame.Rect объектов,
    так как вся карта создается в одном классе  => храниться как единый объект"""
    hit_list = []
    for tile in tiles_list:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

# ---- Нарезка изображения в pygame.image массив ----
def load_tiles(image_file, side):
    # ---- КОНВЕРТАЦИЯ PIL ИЗОБРАДЕНИЯ В PYGAME SURFACE ---- #
    def PILImageToSurface(pilImage):
        return pygame.image.fromstring(
            pilImage.tobytes(), pilImage.size, pilImage.mode).convert_alpha()

    # ---- СОХРАНЕНИЕ ОТДЕЛЬНЫХ ПЛИТОК В МАССИВ ---- #
    image = Image.open(image_file)
    width, height = image.size
    images_list = []

    for y in range(height // side):
        for x in range(width // side):
            left = x * side
            top = y * side
            right = (x + 1) * side
            bottom = (y + 1) * side
            cropped_image = image.crop((left, top, right, bottom))
            images_list.append(PILImageToSurface(cropped_image))

    return images_list
################ КАРТА УРОВНЯ ################
class Map(pygame.sprite.Sprite):
    def __init__(self, map_folder_name):
        super().__init__(map_sprites)
        # ----------- ФОН ----------- #
        self.background_image = pygame.image.load(f'{map_folder_name}/background.jpg').convert()
        self.background_image = pygame.transform.scale(self.background_image, (SURFACE_WIDTH, SURFACE_HEIGHT))
        self.map_folder_name = map_folder_name


        with open(f'{map_folder_name}/txt_map.txt') as file:
            self.map_data = [[int(tile) for tile in row.split(',')] for row in file.read().split('\n')]

        self.tiles_list = load_tiles(image_file=f'{map_folder_name}/tile_set_1.png', side=TILE_SIDE)

    def get_objects(self):
        with open(f"{self.map_folder_name}/objects.json", "r") as read_file:
            data = json.load(read_file)
            return data

    def update(self):
        display.blit(self.background_image, (0, 0))

        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile != -1:
                    self.tile_x = x * TILE_SIDE
                    self.tile_y = y * TILE_SIDE
                    self.tile_image = self.tiles_list[tile]

                    display.blit(self.tile_image, (self.tile_x - camera.offset.x, self.tile_y - camera.offset.y))
                    tile_rects.append(pygame.Rect(self.tile_x, self.tile_y, TILE_SIDE, TILE_SIDE))

################ ПЕРСОНАЖ ################
class Player(pygame.sprite.Sprite):
    def __init__(self, player_image_name, HP):
        super().__init__(player_sprite)

        self.image = pygame.image.load(player_image_name) # Спрайт
        self.rect = self.image.get_rect() # Rect персонажа
        self.collisions_types = {'top': False, 'bottom': False, 'left': False, 'right': False}

        self.currentHP = HP
        self.maxHP = HP
        self.damage = 2

        # Начальные координаты
        self.rect.x = 13 * TILE_SIDE
        self.rect.y = 23 * TILE_SIDE

        # Размер персонажа
        self.width, self.height = self.rect.size
        self.orientation = 'right'

        # Параметры движения по оси Ox
        self.movement = [0, 0]
        self.moving_right, self.moving_left = False, False
        self.speed = 2

        # Параметры прыжка (различные коэффициенты для более гибкой настройки высоты прыжка и тп)
        self.is_jump = False
        self.jump_force = 40
        self.jump_count = 0
        self.jump_coef = 0.2

        self.gravity = 1
        self.acceleration = 0.1

    # Перемещение перосонажа по обоим осям + коллизия с картой
    def player_move(self, tiles):
        self.rect.x += self.movement[0]
        hit_list = collision_test(self.rect, tiles)
        for tile in hit_list:
            if self.movement[0] > 0:
                self.rect.right = tile.left
                self.collisions_types['right'] = True

            elif self.movement[0] < 0:
                self.rect.left = tile.right
                self.collisions_types['left'] = True

        self.rect.y += self.movement[1]
        hit_list = collision_test(self.rect, tiles)
        for tile in hit_list:
            if self.movement[1] > 0:
                self.rect.bottom = tile.top
                self.is_jump = False
                self.collisions_types['bottom'] = True

            elif self.movement[1] < 0:
                self.rect.top = tile.bottom
                self.is_jump = False
                self.collisions_types['top'] = True

    # Прыдок
    def jump(self):
        if self.is_jump:
            if self.jump_count >= 0:
                self.movement[1] -= self.jump_count * self.jump_coef
                self.jump_count -= 1
            else:
                self.is_jump = False

    def shoot(self):
        Bullet(
            bullet_image_name="Assets/Images/bullet.png",
            start_position=self.rect.center,
            finish_position=cursor.rect.center,
            is_camera_offset=True,
            speed=3,
            damage=self.damage,
            target_list=enemy_list,
            rects_list=tile_rects
        )

    def take_damage(self, damage):
        self.currentHP -= damage
        print(self.currentHP)

    # Отрисовываем персонажа
    def blit_player(self):
        x, y = self.rect.x - camera.offset.x, self.rect.y - camera.offset.y

        if self.orientation == 'right':
            display.blit(self.image, (x, y))
        elif self.orientation == 'left':
            display.blit(pygame.transform.flip(self.image, True, False), (x, y))

        player_list.append(self)

    # Цикл персонажа
    def update(self):
        self.movement[0] = 0 # Скорость перемещения перосонажа по обоим осям
        self.collisions_types = {'top': False, 'bottom': False, 'left': False, 'right': False}

        # Перемещение влево/право
        if self.moving_right:
            self.movement[0] += self.speed
        if self.moving_left:
            self.movement[0] -= self.speed

        # Гравитация
        self.movement[1] += self.gravity
        self.gravity += self.acceleration
        # Устанавливаем максимальное значение гравитации
        if self.movement[1] > 3:
            self.movement[1] = 3

        self.jump()
        self.player_move(tile_rects)

        self.blit_player()

################ ПРИЦЕЛ ################
class Cursor(pygame.sprite.Sprite):
    def __init__(self, scope_image_name):
        super().__init__(player_sprite)
        self.image = pygame.image.load(scope_image_name)
        self.rect = self.image.get_rect()

    def update(self):
        mouse_position = pygame.mouse.get_pos()
        self.rect.centerx = mouse_position[0] * (SURFACE_WIDTH / WIDTH)
        self.rect.centery = mouse_position[1] * (SURFACE_HEIGHT / HEIGHT)
        display.blit(self.image, self.rect)

################ ПУЛЯ ################
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_image_name, start_position, finish_position, is_camera_offset, speed, damage, target_list, rects_list=None):
        super().__init__(bullet_group)
        self.image = pygame.image.load(bullet_image_name)

        self.x, self.y = start_position

        if is_camera_offset:
            self.start_position = (start_position[0] - camera.offset.x,
                                   start_position[1] - camera.offset.y)
        else:
            self.start_position = start_position

        self.finish_position = finish_position
        self.speed = speed
        self.damage = damage

        self.target_list = target_list
        self.rects_list = rects_list

        self.dx = self.finish_position[0] - self.start_position[0]
        self.dy = self.finish_position[1] - self.start_position[1]
        self.angle = atan2(self.dy, self.dx)

    def destroy(self):
        if self.rects_list:
            if collision_test(self.rect_to_collide, self.rects_list):
                self.kill()

         # x = self.x - camera.offset.x
        # y = self.y - camera.offset.y
        # if (x < 0 or x > SURFACE_WIDTH) or (y < 0 or y > SURFACE_HEIGHT):
        #     self.kill()

    def hit_target(self):
        if self.target_list:
            hit_list = collision_test(self.rect_to_collide, self.target_list)
            if hit_list:
                hit_list[0].take_damage(self.damage)
                self.kill()

    def move(self):
        self.x += self.speed * cos(self.angle)
        self.y += self.speed * sin(self.angle)

    def draw(self):
        display.blit(self.image, (self.x - camera.offset.x, self.y - camera.offset.y))

    def update(self):
        self.move()

        self.rect_to_collide = pygame.Rect(
            self.x,
            self.y,
            self.image.get_width(),
            self.image.get_height()
        )

        self.hit_target()
        self.destroy()
        self.draw()

################ ВРАГ ################
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image, HP, damage, target):
        super().__init__(enemy_sprites)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.x = x * TILE_SIDE
        self.rect.y = y * TILE_SIDE

        self.currentHP = HP
        self.maxHP = HP

        self.damage = damage
        self.shoot_cd = 2
        self.target = target
        self.min_distance_to_target = 400

        self.start_time = time.time()

    def get_distance_to_target(self):
        dy = self.rect.center[0] - self.target.rect.center[0]
        dx = self.rect.center[1] - self.target.rect.center[1]
        return hypot(dx, dy)

    def shoot_to_player(self):
        if self.get_distance_to_target() < self.min_distance_to_target:
            if time.time() - self.start_time > self.shoot_cd:
                Bullet(
                    bullet_image_name="Assets/Images/enemy_bullet.png",
                    start_position=(self.rect.centerx, self.rect.y),
                    finish_position=self.target.rect.center,
                    is_camera_offset=False,
                    speed=2,
                    damage=self.damage,
                    target_list=player_list,
                    rects_list=None
                )
                # print(self.rect.center, self.target.rect.center)
                self.start_time = time.time()

    def take_damage(self, damage):
        self.currentHP -= damage

    def blit_enemy(self):
        x, y = self.rect.x - camera.offset.x, self.rect.y - camera.offset.y
        if self.rect.x < self.target.rect.x:
            display.blit(self.image, (x, y))
        else:
            display.blit(pygame.transform.flip(self.image, True, False), (x, y))

    def is_dead(self):
        if self.currentHP <= 0:
            self.kill()

class Wizzard(Enemy):
    def __init__(self, x, y, image, HP, damage, target):
        super().__init__(x, y, image, HP, damage, target)

    def update(self):
        enemy_list.append(self)
        self.is_dead()
        self.shoot_to_player()
        self.blit_enemy()






################ КАРТА #################
map = Map(map_folder_name='Maps/Map1')

################ ПЕРСОНАЖ ################
player = Player(player_image_name='Assets/Images/player.png', HP=10) # Персонаж
cursor = Cursor(scope_image_name='Assets/Images/scope.png')

data = map.get_objects()
for x, y in data['enemies']['wizards']['positions']:
    hp = data['enemies']['wizards']['HP']
    damage = data['enemies']['wizards']['damage']
    Wizzard(x=x, y=y, image='Assets/Images/wizzard.png', HP=hp, damage=damage, target=player)


################ КАМЕРА ################
camera = Camera(player=player, width=SURFACE_WIDTH, height=SURFACE_HEIGHT)
follow = Follow(camera, player, smooth=10)
auto = Auto(camera, player, speed=1)
camera.set_method(follow)


################ ИГРОВОЙ ЦИКЛ ################
run = True
while run:
    tile_rects = []
    enemy_list = []
    player_list = []
    map_sprites.update()

    ################ ИГРОВЫЕ СОБЫТИЯ ################
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

        ################ СОБЫТИЯ КЛАВИАТУРЫ ################
        if event.type == pygame.KEYDOWN:
            if event.key == K_d:
                player.moving_right = True
                player.orientation = "right"
            if event.key == K_a:
                player.moving_left = True
                player.orientation = "left"
            if event.key == K_SPACE:
                if player.collisions_types["bottom"] or \
                        player.collisions_types["left"] or \
                        player.collisions_types["right"]:
                    player.is_jump = True
                    player.jump_count = player.jump_force

            if event.key == K_1:
                camera.set_method(border)
            if event.key == K_2:
                camera.set_method(follow)

        if event.type == pygame.KEYUP:
            if event.key == K_d:
                player.moving_right = False
            if event.key == K_a:
                player.moving_left = False

        ################ СОБЫТИЯ МЫШИ ################
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                player.shoot()

    ################ ОБНОВЛЕНИЕ/АНИМАЦИЯ СПРАЙТОВ ################
    all_sprites.update()
    enemy_sprites.update()
    player_sprite.update()
    bullet_group.update()

    ################ КОНТРОЛЬ И ПЕРЕМЕЩЕНИЕ КАМЕРЫ ################
    camera.method_control(max_width=1600, max_height=640, camera_function=follow)
    camera.scroll()

    # Растягиваем display на весь screen
    surface = pygame.transform.scale(display, WINDOW_SIZE)  # WINDOW_SIZE
    screen.blit(surface, (0, 0))

    pygame.display.flip()
    clock.tick(FPS)

    # print(player.rect.x - camera.offset.x)
    # print(str(int(clock.get_fps())))

pygame.quit()
