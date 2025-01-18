import pygame
from config import CAR_HEIGHT, CAR_WIDTH


class Car:
    def __init__(self, screen):
        self._car = pygame.image.load("./sprites/car.png").convert_alpha()
        self._car = pygame.transform.scale(self._car, size=(CAR_WIDTH, CAR_HEIGHT))
        self._car = pygame.transform.rotate(self._car, 90)
        # Copy used to rotate the car object from the original sprite instead of compounding rotations
        # as this will deform the original image in unexpected ways.
        self._car_copy = self._car
        self._car_rect = self._car.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        self._angle = 0

    @property
    def car(self):
        return self._car

    @property
    def car_rect(self):
        return self._car_rect

    @property
    def rect_pos(self):
        return [self._car_rect.x, self._car_rect.y]

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    @car.setter
    def car(self, value):
        self._car = value

    @car_rect.setter
    def car_rect(self, value):
        self._car_rect = value

    def adjust_angle(self, angle_modifier):
        self._angle += angle_modifier
        self._car = pygame.transform.rotate(self._car_copy, self._angle)
        # Re-center the sprite everytime its angle changes to simulate rotation about its center.
        # Otherwise, rotation happens about its top-left co-ordinate
        self._car_rect = self._car.get_rect(center=self._car_rect.center)
