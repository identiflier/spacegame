import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the window

'''
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 700
'''

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window_width, window_height = pygame.display.get_surface().get_size()
pygame.display.set_caption("Space Shooter")

# Set some constants
SPEED_OF_LIGHT = 10

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

class Ship:
    def __init__(self, position=[0, 0], accel = 0.01):
        self.world_pos = position
        self.vel = [0, 0]
        #real_vel is the ship's speed after applying the speed of light limit
        self.real_vel = [0, 0]
        self.accel = accel
        self.radius = 10

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
        
        #adjust for speed of light limit
        self.real_vel[0] = apply_sol(self.vel[0])
        self.real_vel[1] = apply_sol(self.vel[1])

        # adjust position
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

p1 = TestPoint()
p2 = TestPoint([500, 0])
myship = Ship()
bullets = []

class Game:
    def __init__(self):
        self.camera = Camera()
        self.playership = myship
        self.camera.following = self.playership
        self.clock = pygame.time.Clock()
    
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
                

            # Update things
            self.camera.update()
            self.playership.update()
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

# Start the game
game = Game()
game.run()