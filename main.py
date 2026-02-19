import math
import sys

import pygame


WIDTH, HEIGHT = 900, 700
FPS = 60

BACKGROUND = (20, 25, 35)
ROD_COLOR = (230, 230, 230)
BOB_COLOR = (225, 110, 80)
ANCHOR_COLOR = (120, 220, 245)
TEXT_COLOR = (240, 240, 240)

GRAVITY = 9.81
PIXELS_PER_METER = 180
DAMPING = 0.998

    @property
    def bob_weight_newtons(self):
        return self.mass * GRAVITY

# Requested pendulum settings
BALL_MASS = 3.0  # kg
ROD_LENGTH = 1.7  # meters
INITIAL_ANGLE_DEG = 45


class Pendulum:
    def __init__(self, anchor, length_m, mass_kg, initial_angle_rad):
        self.anchor = pygame.Vector2(anchor)
        self.length = length_m
        self.mass = mass_kg
        self.theta = initial_angle_rad
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0

    def update(self, dt):
        # Equation of motion for a simple pendulum.
        self.angular_acceleration = -(GRAVITY / self.length) * math.sin(self.theta)
        self.angular_velocity += self.angular_acceleration * dt
        self.angular_velocity *= DAMPING
        self.theta += self.angular_velocity * dt

    @property
    def bob_position(self):
        length_px = self.length * PIXELS_PER_METER
        x = self.anchor.x + length_px * math.sin(self.theta)
        y = self.anchor.y + length_px * math.cos(self.theta)
        return pygame.Vector2(x, y)

    @property
    def bob_radius(self):
        return int(16 + self.mass * 3)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Pendulum Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)

pendulum = Pendulum(
    anchor=(WIDTH // 2, 150),
    length_m=ROD_LENGTH,
    mass_kg=BALL_MASS,
    initial_angle_rad=math.radians(INITIAL_ANGLE_DEG),
)

running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                pendulum.theta = math.radians(INITIAL_ANGLE_DEG)
                pendulum.angular_velocity = 0.0

    pendulum.update(dt)

    screen.fill(BACKGROUND)

    bob = pendulum.bob_position
    pygame.draw.line(screen, ROD_COLOR, pendulum.anchor, bob, 4)
    pygame.draw.circle(screen, ANCHOR_COLOR, pendulum.anchor, 10)
    pygame.draw.circle(screen, BOB_COLOR, bob, pendulum.bob_radius)

    info = [
        f"Ball mass: {pendulum.mass:.1f} kg",
        f"Rod length: {pendulum.length:.2f} m",
        f"Angle: {math.degrees(pendulum.theta):.1f} deg",
        "Press R to reset, ESC to quit",
    ]

    for i, line in enumerate(info):
        surface = font.render(line, True, TEXT_COLOR)
        screen.blit(surface, (20, 20 + i * 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
            f"Ball weight: {self.pendulum.bob_weight_newtons:.1f} N",
