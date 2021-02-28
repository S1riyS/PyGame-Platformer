import pygame
from abc import ABC, abstractmethod

if __name__ == '__main__':
    from data import *
else:
    from Modules.data import *

vec = pygame.math.Vector2

################# ОСНОВНОЙ КЛАСС КАМЕРЫ #################
class Camera:
    def __init__(self, player, width, height):
        self.player = player
        self.WIDTH, self.HEIGHT = width, height

        self.offset = vec(0, 0)
        self.offset_float = vec(0, 0)
        self.CONST = vec(-(self.WIDTH / 3), -(self.HEIGHT - self.player.rect.height) / 2)

        print(self.CONST)

    def set_method(self, method):
        self.method = method

    def scroll(self):
        self.method.scroll()

    def method_control(self, max_width, max_height, camera_function):
        left_border = self.player.rect.x + self.CONST.x
        right_border = self.WIDTH + self.CONST.x + self.player.rect.x

        top_border = self.player.rect.y + self.CONST.y
        bottom_border = self.HEIGHT + self.CONST.y + self.player.rect.y
        if (left_border <= 0) or (right_border >= max_width):
            camera_function.stop_x_movement = True
        else:
            camera_function.stop_x_movement = False

        if (top_border <= 0) or (bottom_border >= max_height):
            camera_function.stop_y_movement = True
        else:
            camera_function.stop_y_movement = False


################# СОСТОЯНИЯ КАМЕРЫ #################
class CamScroll(ABC):
    def __init__(self, camera, player):
        self.camera = camera
        self.player = player

    @abstractmethod
    def scroll(self):
        pass


class Follow(CamScroll):
    def __init__(self, camera, player, smooth):
        CamScroll.__init__(self, camera, player)
        self.smooth = smooth
        self.stop_x_movement, self.stop_y_movement = False, False

    def scroll(self):
        if not self.stop_x_movement:
            self.camera.offset_float.x += (
                self.player.rect.x - self.camera.offset_float.x + self.camera.CONST.x
            ) // self.smooth
        if not self.stop_y_movement:
            self.camera.offset_float.y += (
                self.player.rect.y - self.camera.offset_float.y + self.camera.CONST.y
            ) // self.smooth
        self.camera.offset.x, self.camera.offset.y = (
            int(self.camera.offset_float.x),
            int(self.camera.offset_float.y),
        )


class Border(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)
        self.stop_x_movement, self.stop_y_movement = False, False

    def scroll(self):
        if not self.stop_x_movement:
            self.camera.offset_float.x += self.player.rect.x - self.camera.offset_float.x + self.camera.CONST.x

        if not self.stop_y_movement:
            self.camera.offset_float.y += self.player.rect.y - self.camera.offset_float.y + self.camera.CONST.y

        self.camera.offset.x, self.camera.offset.y = (
            int(self.camera.offset_float.x),
            int(self.camera.offset_float.y),
        )

        # self.camera.offset.x = max(self.player.rect.left, self.camera.offset.x)
        # self.camera.offset.x = min(self.camera.offset.x, self.player.rect.right - self.camera.WIDTH)


class Auto(CamScroll):
    def __init__(self, camera, player, speed):
        CamScroll.__init__(self, camera, player)
        self.speed = speed

    def scroll(self):
        self.camera.offset.x += self.speed
