import pygame
from math import e, pow, sin, cos, radians
import pytmx
from config import *
from car import Car


# pygame setup:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('DK')


def move(speed, angle, dt):
    # Movement follows the angle of the car. E.g. When the car is angled at 90 deg,
    # sin(90) = 1, cos(90) = 0, therefore x-axis multiplied by 1, y-axis multiplied by 0.
    # In other words, maximum horizontal movement and minimum vertical movement.
    x = sin(radians(angle)) * speed * dt
    y = cos(radians(angle)) * speed * dt

    return [x, y]


def lap_time(start_time, end_time):
    pass


def seconds_to_time(seconds):
    if seconds != float('inf'):
        minutes = int(seconds/60)
        return f"{minutes}:{int(seconds) - minutes*60}"

    return seconds


def main():
    clock = pygame.time.Clock()
    running = True

    collision = False
    dt = 0
    current_speed = 0
    t = 0  # time elapsed since acceleration / deceleration

    # lap variables
    font = pygame.font.Font(None, 36)
    lap_count = 0
    lap_time_start = 0  # Time right after crossing the start / finish line
    lap_time_elapsed = 0  # Real time
    lap_time = float('inf')  # Total time taken to complete one lap
    best_time = float('inf')
    best_lap = 0
    timer_running = False

    # Finish line collision rectangle position
    finish_line = pygame.Surface((5, 217), pygame.SRCALPHA)
    finish_line_x = 285
    finish_line_y = 60

    # Load background
    bg = pytmx.load_pygame('./tileset/map.tmx')
    # Get map dimensions
    tile_width = bg.tilewidth
    tile_height = bg.tileheight
    map_width = bg.width * tile_width
    map_height = bg.height * tile_height
    # Calculate offsets for centering the map
    map_offset_x = (screen.get_width() - map_width) // 2
    map_offset_y = (screen.get_height() - map_height) // 2

    # Game loop
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        offset = move(current_speed, car.angle, dt)
        map_offset_x += offset[0]
        map_offset_y += offset[1]
        finish_line_x += offset[0]
        finish_line_y += offset[1]
        # Rect object for collision detection
        finish_line_rect = finish_line.get_rect(topleft=(finish_line_x, finish_line_y))

        for layer in bg.visible_layers:
            for x, y, gid, in layer.tiles():
                # tile = bg.get_tile_image_by_gid(gid)
                # if tile:
                screen_x = x * tile_width + map_offset_x
                screen_y = y * tile_height + map_offset_y
                screen.blit(gid, (screen_x, screen_y))

        # Used to reset the car co-ords in case it gets out of bounds.
        prev_car_pos_x = car.car_rect.x
        prev_car_pos_y = car.car_rect.y

        # Car movement & angle
        key = pygame.key.get_pressed()
        # Decrease max speed while turning
        if key[pygame.K_a] or key[pygame.K_d]:
            max_speed = TURN_SPEED
            if current_speed > max_speed:
                t = 1
        else:
            max_speed = MAX_SPEED

        velocity = (1 - pow(e, -ACCELERATION * t))

        if key[pygame.K_w] and not key[pygame.K_s]:
            t += dt
            # if current_speed < max_speed / 2:
            #     current_speed += ACCELERATION/2 * dt
            # elif max_speed / 2 < current_speed < max_speed:
            #     current_speed += ACCELERATION * dt
            # else:
            #     current_speed -= ACCELERATION * dt
            if current_speed > max_speed:
                current_speed -= max_speed * velocity
            else:
                current_speed += max_speed * velocity

        if key[pygame.K_s] and not key[pygame.K_w]:
            t += dt
            # if current_speed > -max_speed/2:
            #     current_speed -= ACCELERATION/2 * dt
            # elif max_speed/2 < current_speed < max_speed:
            #     current_speed -= ACCELERATION * dt
            # else:
            #     current_speed += ACCELERATION * dt
            if current_speed > -max_speed:
                current_speed -= max_speed * velocity
            else:
                current_speed += max_speed * velocity

        if key[pygame.K_a] and current_speed != 0:
            if current_speed <= (max_speed/2):
                angle_modifier = current_speed * ANGLE_MULTIPLIER
            else:
                angle_modifier = (max_speed/2) * ANGLE_MULTIPLIER
            car.adjust_angle(angle_modifier)

        if key[pygame.K_d] and current_speed != 0:
            if current_speed <= (max_speed/2):
                angle_modifier = current_speed * -ANGLE_MULTIPLIER
            else:
                angle_modifier = (max_speed/2) * -ANGLE_MULTIPLIER
            car.adjust_angle(angle_modifier)

        if key[pygame.K_SPACE] and current_speed > 0:
            current_speed -= BRAKE_POWER * velocity
        elif key[pygame.K_SPACE] and current_speed < 0:
            current_speed += BRAKE_POWER * velocity

        # Handle deceleration by gradually decrementing or
        # incrementing speed (depending on what direction the car was going before)
        if not (key[pygame.K_w] or key[pygame.K_s]):
            current_speed *= (1 - FRICTION * dt)

        # Ensure the car stays within the screen boundaries
        if not (0 <= car.car_rect.x <= (screen.get_width() - CAR_WIDTH) and
                0 <= car.car_rect.y <= (screen.get_height() - CAR_WIDTH)):
            car.car_rect.x = prev_car_pos_x
            car.car_rect.y = prev_car_pos_y

        # print(current_speed)

        # Finish line collision logic
        if finish_line_rect.colliderect(car.car_rect):
            collision = True
        else:
            if collision:
                timer_running = True
                lap_count += 1
                lap_time = (pygame.time.get_ticks() - lap_time_start) / 1000  # Convert to seconds
                lap_time_start = pygame.time.get_ticks()
            collision = False

        # Timer
        if lap_time < best_time:
            best_time = lap_time
            best_lap = lap_count - 1

        if timer_running:
            lap_time_elapsed = (pygame.time.get_ticks() - lap_time_start) / 1000  # Convert to seconds
        timer_text = font.render(f"Time: {seconds_to_time(lap_time_elapsed)}", True, 'black')
        timer_text_rect = timer_text.get_rect(center=(SCREEN_WIDTH/2, 50))
        lap_time_text = font.render(f"Best lap: {seconds_to_time(best_time)} on lap {best_lap}",
                                    True, 'black')
        lap_time_text_rect = lap_time_text.get_rect(center=(SCREEN_WIDTH/1.2, 50))

        # Display
        screen.blit(lap_time_text, lap_time_text_rect)
        screen.blit(timer_text, timer_text_rect)
        screen.blit(finish_line, (finish_line_x, finish_line_y))
        screen.blit(car.car, car.rect_pos)  # (car object, coordinates)
        # pygame.draw.rect(screen, 'red', car.car_rect, 2)
        pygame.display.flip()
        dt = clock.tick(60) / 1000  # limits FPS to 60


if __name__ == "__main__":
    car = Car(screen)
    main()
    pygame.quit()
