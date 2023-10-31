import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the window


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400


# Choose windown mode (Comment out the mode you don't want)
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

window_width, window_height = pygame.display.get_surface().get_size()
pygame.display.set_caption("Space Shooter")

# Initialize the joysticks
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

# Set some constants
SPEED_OF_LIGHT = 10
SHIP_ACCELERATION = 0.1
TURRET_LENGTH = 15

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Camera:
    def __init__(self):
        self.world_pos = [0, 0]
        self.following = None
        self.zoom = 1.0

    def world_to_screen(self, world_pos):
        # Calculate the position of the world point relative to the camera
        rel_x = world_pos[0] - self.world_pos[0]
        rel_y = world_pos[1] - self.world_pos[1]

        # Invert the y-coordinate relative to the camera
        rel_y = -rel_y

        # Apply the camera zoom
        rel_x *= self.zoom
        rel_y *= self.zoom

        # Calculate the screen position
        screen_x = window_width / 2 + rel_x
        screen_y = window_height / 2 + rel_y

        return (int(screen_x), int(screen_y))
    
    def screen_to_world(self, screen_pos):
        # Calculate the position of the screen point relative to the center of the screen
        rel_x = screen_pos[0] - window_width / 2
        rel_y = screen_pos[1] - window_height / 2

        # Apply the camera zoom
        rel_x /= self.zoom
        rel_y /= self.zoom

        # Invert the y-coordinate relative to the camera
        rel_y = -rel_y

        # Calculate the world position
        world_x = self.world_pos[0] + rel_x
        world_y = self.world_pos[1] + rel_y

        return (world_x, world_y)

    def update(self):
        self.follow(self.following)
        
    def follow(self, target):
        self.world_pos = target.world_pos

    def draw_circle(self, world_pos, size, color=WHITE):
        screen_pos = self.world_to_screen(world_pos)
        scaled_size = size * self.zoom
        if scaled_size < 1:
            scaled_size = 1
        pygame.draw.circle(window, color, screen_pos, scaled_size)

    def draw_line(self, world_pos1, world_pos2, color=WHITE, width=1):
        screen_pos1 = self.world_to_screen(world_pos1)
        screen_pos2 = self.world_to_screen(world_pos2)
        pygame.draw.line(window, color, screen_pos1, screen_pos2, width)

class Ship:
    def __init__(self, position=[0, 0], accel = SHIP_ACCELERATION):
        self.game = None
        self.controller = None
        self.turret_length = TURRET_LENGTH
        self.world_pos = position
        self.vel = [0, 0]
        #real_vel is the ship's speed after applying the speed of light limit
        self.real_vel = [0, 0]
        self.accel = accel
        self.radius = 10
        self.angle = 0


    def update(self):
        keys = pygame.key.get_pressed()
        
        # apply acceleration 
        if keys[pygame.K_w]:
            self.vel[1] += self.accel
        if keys[pygame.K_s]:
            self.vel[1] -= self.accel
        if keys[pygame.K_a]:
            self.vel[0] -= self.accel
        if keys[pygame.K_d]:
            self.vel[0] += self.accel

        # Apply left joystick
        self.vel[0] += self.controller.left_stick[0] * self.accel
        self.vel[1] -= self.controller.left_stick[1] * self.accel

        # Adjust for speed of light limit
        self.real_vel[0] = apply_sol(self.vel[0])
        self.real_vel[1] = apply_sol(self.vel[1])

        # Adjust angle
        self.angle = math.atan2(-self.controller.right_stick[1], self.controller.right_stick[0])

        # Adjust position
        self.world_pos[0] += self.real_vel[0]
        self.world_pos[1] += self.real_vel[1]

class Bullet:
    def __init__(self, position=[0, 0], angle=0):
        self.world_pos = position
        self.vel = [math.cos(angle) * SPEED_OF_LIGHT, math.sin(angle) * SPEED_OF_LIGHT]
        self.radius = 5

    def update(self):
        self.world_pos[0] += self.vel[0]
        self.world_pos[1] += self.vel[1]

class TestPoint:
    def __init__(self, position=[0, 0]):
        self.world_pos = position
        self.radius = 10

class Controller:
    def __init__(self):
        self.joystick = None
        self.ship = None
        self.buttons = []
        self.axes = []
        self.hats = []
        self.left_stick = [0, 0]
        self.right_stick = [0, 0]
        self.right_trigger = -1
        self.already_shot = False
    
    def update(self):
        if self.right_trigger > 0 and not self.already_shot:
            self.already_shot = True
            bullets.append(Bullet(self.ship.world_pos.copy(), self.ship.angle))
        if self.right_trigger <= 0:
            self.already_shot = False

class Game:
    def __init__(self):
        self.camera = Camera()
        self.playership = Ship()
        self.camera.following = self.playership
        self.clock = pygame.time.Clock()
        self.controller = Controller()
    
    def run(self):
        # Main game loop
        while True:

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if event.key == pygame.K_SPACE:
                        print(self.camera.world_pos)
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.camera.zoom *= 1.1
                    elif event.y < 0:
                        self.camera.zoom /= 1.1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = self.playership.world_pos.copy()
                        click_world_pos = self.camera.screen_to_world(event.pos)
                        angle = math.atan2(click_world_pos[1] - pos[1], click_world_pos[0] - pos[0])
                        bullets.append(Bullet(pos, angle))
                
                if event.type == pygame.JOYBUTTONDOWN:
                    print(event)
                if event.type == pygame.JOYAXISMOTION:
                    #print(event)
                    if event.axis == 0:
                        self.controller.left_stick[0] = event.value
                    if event.axis == 1:
                        self.controller.left_stick[1] = event.value
                    if event.axis == 2:
                        self.controller.right_stick[0] = event.value
                    if event.axis == 3:
                        self.controller.right_stick[1] = event.value
                    if event.axis == 5:
                        self.controller.right_trigger = event.value
                if event.type == pygame.JOYHATMOTION:
                    print(event)                

            # Update things
            self.camera.update()
            self.playership.update()
            self.controller.update()
            for bullet in bullets:
                bullet.update()

            self.draw()

            # Delay to achieve 60 frames per second
            self.clock.tick(60)



    def draw(self):
        # Clear the screen
        window.fill(BLACK)

        # Draw the ship, bullets, and enemies
        self.camera.draw_circle(p1.world_pos, 10)
        self.camera.draw_circle(p2.world_pos, 10)
        self.camera.draw_circle(self.playership.world_pos, self.playership.radius, GREEN)
        turret_pos_x = self.playership.world_pos[0] + math.cos(self.playership.angle) * self.playership.turret_length
        turret_pos_y = self.playership.world_pos[1] + math.sin(self.playership.angle) * self.playership.turret_length
        self.camera.draw_line(self.playership.world_pos, [turret_pos_x, turret_pos_y], GREEN, int(5 * self.camera.zoom))
        self.camera
        for bullet in bullets:
            self.camera.draw_circle(bullet.world_pos, bullet.radius, RED)

        # Update the display
        pygame.display.update()

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

def apply_sol(speed):
    sol = SPEED_OF_LIGHT
    slope = 1 / sol
    if speed < 0:
        return -sol * (1-math.e**(slope*speed))
    else:
        return sol * (1-math.e**(-slope*speed))

p1 = TestPoint()
p2 = TestPoint([500, 0])
bullets = []

# Start the game
game = Game()

# Attach objects together
game.playership.game = game
game.playership.controller = game.controller
game.controller.ship = game.playership

# Run the game
game.run()