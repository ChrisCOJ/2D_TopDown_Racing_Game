import pygame
from math import sin, cos, radians
import pytmx

CAR_WIDTH = 80  # pixels
CAR_HEIGHT = 40  # pixels
ACCELERATION = 200  # Higher number = faster acceleration
MAX_SPEED = 700  # Arbitrary number, no correlation to mph / kph
TURN_SPEED = 500
BRAKE_POWER = 400
FRICTION = 100  # Higher number = faster idle deceleration
ANGLE_MULTIPLIER = 0.5  # Used to determine rotational velocity in relation to current speed

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption('DK')
clock = pygame.time.Clock()
running = True
dt = 0
current_speed = 0
drift_angle = 0
angle_modifier = 0

# Finish line collision rectangle
finish_line = pygame.Surface((70, 217))
finish_line.fill('red')
finish_line_rect = finish_line.get_rect(center=(640, 348))

# Load background
bg = pytmx.load_pygame('./tileset/map.tmx')
# Get map dimensions
tile_width = bg.tilewidth
tile_height = bg.tileheight
map_width = bg.width * tile_width
map_height = bg.height * tile_height
# Calculate offsets for centering the map
offset_x = (screen.get_width() - map_width) // 2
offset_y = (screen.get_height() - map_height) // 2


class Car:
    def __init__(self):
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


car = Car()


def move(speed, angle, offset_x, offset_y, dt):
    # Movement follows the angle of the car. E.g. When the car is angled at 90 deg,
    # sin(90) = 1, cos(90) = 0, therefore x-axis multiplied by 1, y-axis multiplied by 0.
    # In other words, maximum horizontal movement and minimum vertical movement.
    offset_x += sin(radians(angle)) * speed * dt
    offset_y += cos(radians(angle)) * speed * dt

    return [offset_x, offset_y]


def lap_time(start_time, end_time):
    pass


# Game loop
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for layer in bg.visible_layers:
        for x, y, gid, in layer.tiles():
            # tile = bg.get_tile_image_by_gid(gid)
            # if tile:
            screen_x = x * tile_width + offset_x
            screen_y = y * tile_height + offset_y
            screen.blit(gid, (screen_x, screen_y))

    # Used to reset the car co-ords in case it gets out of bounds.
    prev_car_pos_x = car.car_rect.x
    prev_car_pos_y = car.car_rect.y

    # Car movement & angle
    key = pygame.key.get_pressed()
    # Decrease max speed while turning
    if key[pygame.K_a] or key[pygame.K_d]:
        max_speed = TURN_SPEED
    else:
        max_speed = MAX_SPEED

    if key[pygame.K_w] and not key[pygame.K_s]:
        if current_speed < max_speed / 2:
            current_speed += ACCELERATION/2 * dt
        elif max_speed / 2 < current_speed < max_speed:
            current_speed += ACCELERATION * dt
        else:
            current_speed -= ACCELERATION * dt

    if key[pygame.K_s] and not key[pygame.K_w]:
        if current_speed > -max_speed/2:
            current_speed -= ACCELERATION/2 * dt
        elif max_speed/2 < current_speed < max_speed:
            current_speed -= ACCELERATION * dt
        else:
            current_speed += ACCELERATION * dt

    if key[pygame.K_a] and current_speed != 0:
        if current_speed <= (MAX_SPEED/2):
            angle_modifier = current_speed * ANGLE_MULTIPLIER * dt
        else:
            angle_modifier = (MAX_SPEED/2) * ANGLE_MULTIPLIER * dt
        car.adjust_angle(angle_modifier)

    if key[pygame.K_d] and current_speed != 0:
        if current_speed <= (MAX_SPEED/2):
            angle_modifier = current_speed * -ANGLE_MULTIPLIER * dt
        else:
            angle_modifier = (MAX_SPEED/2) * -ANGLE_MULTIPLIER * dt
        car.adjust_angle(angle_modifier)

    if key[pygame.K_SPACE] and current_speed > 0:
        current_speed -= BRAKE_POWER * dt
    elif key[pygame.K_SPACE] and current_speed < 0:
        current_speed += BRAKE_POWER * dt

    # Handle deceleration by gradually decrementing or
    # incrementing speed (depending on what direction the car was going before)
    if not (key[pygame.K_w] or key[pygame.K_s]):
        if current_speed > 0:
            current_speed -= FRICTION * dt
        elif current_speed < 0:
            current_speed += FRICTION * dt

    # Ensure the car stays within the screen boundaries
    if not (0 <= car.car_rect.x <= (screen.get_width() - CAR_WIDTH) and
            0 <= car.car_rect.y <= (screen.get_height() - CAR_WIDTH)):
        car.car_rect.x = prev_car_pos_x
        car.car_rect.y = prev_car_pos_y

    offset = move(current_speed, car.angle, offset_x, offset_y, dt)
    offset_x = offset[0]
    offset_y = offset[1]
    finish_line_rect.x += offset_x
    finish_line_rect.y += offset_y

    screen.blit(finish_line, finish_line_rect)
    screen.blit(car.car, car.rect_pos)  # (car object, coordinates)
    # pygame.draw.rect(screen, 'red', car.car_rect, 2)

    pygame.display.flip()
    dt = clock.tick(60) / 1000  # limits FPS to 60

pygame.quit()
