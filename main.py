import math
import sys

import pygame

WIDTH, HEIGHT = 900, 700
FPS = 60

BACKGROUND_COLOR = (16, 20, 28)
ROD_COLOR = (220, 230, 245)
BOB_COLOR = (247, 180, 67)
TEXT_COLOR = (225, 232, 245)
ANCHOR_COLOR = (120, 160, 255)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


class Pendulum:
    def __init__(self, origin: tuple[int, int], length: float, mass: float, angle_degrees: float):
        self.origin = pygame.Vector2(origin)
        self.length = length
        self.mass = mass
        self.angle = math.radians(angle_degrees)
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0

        # Gravity and damping are tuned for a smooth classroom-style simulation.
        self.gravity = 9.81
        self.damping = 0.998

    def update(self, dt: float) -> None:
        self.angular_acceleration = -(self.gravity / self.length) * math.sin(self.angle)
        self.angular_velocity += self.angular_acceleration * dt
        self.angular_velocity *= self.damping
        self.angle += self.angular_velocity * dt

    def bob_position(self) -> pygame.Vector2:
        x = self.origin.x + self.length * math.sin(self.angle)
        y = self.origin.y + self.length * math.cos(self.angle)
        return pygame.Vector2(x, y)

    def set_length(self, length: float) -> None:
        self.length = clamp(length, 80, 360)

    def set_mass(self, mass: float) -> None:
        self.mass = clamp(mass, 0.5, 15.0)

    def tension(self) -> float:
        tangential_speed = self.angular_velocity * self.length
        centripetal = (self.mass * tangential_speed**2) / self.length
        gravity_component = self.mass * self.gravity * math.cos(self.angle)
        return max(0.0, centripetal + gravity_component)


def draw_text(screen: pygame.Surface, font: pygame.font.Font, text: str, position: tuple[int, int]) -> None:
    rendered = font.render(text, True, TEXT_COLOR)
    screen.blit(rendered, position)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Pendulum Physics Simulation")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

    pendulum = Pendulum(origin=(WIDTH // 2, 120), length=250.0, mass=4.0, angle_degrees=35.0)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    pendulum.angle = math.radians(35)
                    pendulum.angular_velocity = 0.0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            pendulum.set_length(pendulum.length + 60 * dt)
        if keys[pygame.K_DOWN]:
            pendulum.set_length(pendulum.length - 60 * dt)
        if keys[pygame.K_RIGHT]:
            pendulum.set_mass(pendulum.mass + 3.0 * dt)
        if keys[pygame.K_LEFT]:
            pendulum.set_mass(pendulum.mass - 3.0 * dt)

        pendulum.update(dt)

        screen.fill(BACKGROUND_COLOR)

        bob = pendulum.bob_position()
        bob_radius = int(18 + pendulum.mass * 1.8)

        pygame.draw.line(screen, ROD_COLOR, pendulum.origin, bob, 4)
        pygame.draw.circle(screen, ANCHOR_COLOR, pendulum.origin, 8)
        pygame.draw.circle(screen, BOB_COLOR, bob, bob_radius)

        draw_text(screen, font, "Arrow Up/Down: line length", (40, 30))
        draw_text(screen, font, "Arrow Left/Right: bob weight", (40, 60))
        draw_text(screen, font, "R: reset angle   Esc: quit", (40, 90))

        draw_text(screen, font, f"Line length: {pendulum.length:6.1f} px", (40, HEIGHT - 120))
        draw_text(screen, font, f"Ball weight (mass): {pendulum.mass:5.2f} kg", (40, HEIGHT - 90))
        draw_text(screen, font, f"Current tension: {pendulum.tension():7.2f} N", (40, HEIGHT - 60))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
