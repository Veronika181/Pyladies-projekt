import random
import math
from pyglet import gl
from math import sin, cos, degrees
import pyglet
from pyglet.gl import *
import pygame

pygame.font.init()

"Nastavení hry"
ROTATION_SPEED = 3
ACCELERATION = 20
ASTEROID_SPEED = 60
ASTEROID_ROTATION_SPEED = 1
LASER_SPEED = 600
SHOOT_INTERVAL = 0.2

window = pyglet.window.Window(width=1000, height=800)
score = 0


def load_image(path):
    image = pyglet.image.load(path)
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    return image


image = load_image("PNG/playerShip3_red.png")
laser_image = load_image("PNG/Lasers/laserGreen10.png")

"""Zatím nefunguje vyobrazení pygame pozadí
pygame.init()
screen = pygame.display.set_mode((800, 600))
background = pygame.image.load("PNG/Background/purple.png")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(background, (0, 0))
    pygame.display.update()"""

"Zmáčknutí kláves"
pressed_keys = set()

"Vykresluje kruh objektu"


def draw_circle(x, y, radius):
    iterations = 20
    s = math.sin(2 * math.pi / iterations)
    c = math.cos(2 * math.pi / iterations)

    dx, dy = radius, 0

    pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
    for i in range(iterations + 1):
        pyglet.gl.glVertex2f(x + dx, y + dy)
        dx, dy = (dx * c - dy * s), (dy * c + dx * s)
    pyglet.gl.glEnd()


"Střet s objekty"


def distance(a, b, wrap_size):
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result


def overlaps(a, b):
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = (a.radius + b.radius) ** 2
    return distance_squared < max_distance_squared


"Hlavní objekt"


class Main_object:
    def __init__(self, image):
        self.x = 0
        self.y = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rotation = 0
        self.rotation_speed = 0
        self.radius = 30

        self.sprite = pyglet.sprite.Sprite(image)

    def draw(self):
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.rotation = 90 - degrees(self.rotation)
        self.sprite.draw()

    "Nastavení pohybu objektu"

    def tick(self, dt):
        self.x = self.x + self.speed_x * dt
        self.y = self.y + self.speed_y * dt
        self.rotation = self.rotation + self.rotation_speed * dt

        self.x = self.x % window.width
        self.y = self.y % window.height

    "Odstraní objekt"

    def delete(self):
        try:
            objects.remove(self)
        except ValueError:
            pass

    def hit_by_spaceship(self, ship):
        pass

    def hit_by_laser(self, ship):
        pass

    "Třída raketa"


class Rocket(Main_object):
    def __init__(self):
        super().__init__(image)
        self.x = window.width / 2
        self.y = window.height / 2
        self.next_shot = 0

    def tick(self, dt):
        super().tick(dt)
        if pyglet.window.key.LEFT in pressed_keys:
            self.rotation = self.rotation + ROTATION_SPEED * dt
        if pyglet.window.key.RIGHT in pressed_keys:
            self.rotation = self.rotation - ROTATION_SPEED * dt
        if pyglet.window.key.UP in pressed_keys:
            self.speed_x = self.speed_x + ACCELERATION * cos(self.rotation)
            self.speed_y = self.speed_y + ACCELERATION * sin(self.rotation)
        if pyglet.window.key.SPACE in pressed_keys and self.next_shot <= 0:
            laser = Laser(self)
            objects.append(laser)
            self.next_shot = SHOOT_INTERVAL
        self.next_shot = self.next_shot - dt

        for obj in list(objects):
            if overlaps(self, obj):
                obj.hit_by_spaceship(self)

    "Třída laser"


class Laser(Main_object):
    def __init__(self, ship):
        super().__init__(laser_image)
        self.radius = 20
        self.x = ship.x
        self.y = ship.y
        self.rotation = ship.rotation
        self.speed_x = ship.speed_x + LASER_SPEED * cos(self.rotation)
        self.speed_y = ship.speed_y + LASER_SPEED * sin(self.rotation)

    def tick(self, dt):
        super().tick(dt)
        for obj in list(objects):
            if overlaps(self, obj):
                obj.hit_by_laser(self)

        "Třída asteroid"


class Asteroid(Main_object):
    def __init__(self, size):
        if size == 3:
            size_name = 'big'
            variant = random.choice([1, 2, 3, 4])
            radius = 40
        elif size == 2:
            size_name = 'med'
            variant = random.choice([1, 2])
            radius = 20
        elif size == 1:
            size_name = 'small'
            variant = random.choice([1, 2])
            radius = 10
        else:
            raise ValueError('špatná velikost!')
        image = load_image(f"PNG/Meteors/meteorGrey_{size_name}{variant}.png")
        super().__init__(image)
        self.x = random.uniform(0, window.width)
        self.speed_x = random.uniform(-ASTEROID_SPEED, ASTEROID_SPEED)
        self.speed_y = random.uniform(-ASTEROID_SPEED, ASTEROID_SPEED)
        self.rotation_speed = random.uniform(
            -ASTEROID_ROTATION_SPEED, ASTEROID_ROTATION_SPEED)
        self.radius = radius
        self.size = size

    def hit_by_spaceship(self, ship):
        ship.delete()

    def hit_by_laser(self, laser):
        score = 0
        self.delete()
        laser.delete()
        new_size = self.size - 1
        if new_size > 0:
            for i in range(2):
                new_asteroid = Asteroid(new_size)
                new_asteroid.x = self.x
                new_asteroid.y = self.y
                new_asteroid.speed_x = self.speed_x + random.uniform(
                    -ASTEROID_SPEED, ASTEROID_SPEED)
                new_asteroid.speed_y = self.speed_y + random.uniform(
                    -ASTEROID_SPEED, ASTEROID_SPEED)
                objects.append(new_asteroid)



raketa = Rocket()


def tick(dt):
    for obj in objects:
        obj.tick(dt)


pyglet.clock.schedule_interval(tick, 1 / 30)

objects = [Rocket(), Asteroid(3), Asteroid(3)]


@window.event
def on_key_press(key, mod):
    pressed_keys.add(key)
    print(pressed_keys)


@window.event
def on_key_release(key, mod):
    pressed_keys.discard(key)
    print(pressed_keys)


@window.event
def on_draw():
    window.clear()
    for obj in objects:
        obj.draw()
        draw_circle(obj.x, obj.y, obj.radius)


pyglet.app.run()
