import pygame
from game.world import Platform

SPEED = 4
GRAVITY = 0.55
MAX_FALL_SPEED = 12
JUMP_STRENGTH = -13


class Player:
    """Represents player character physics and collisions."""

    def __init__(self, x: float, y: float):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0.0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms: list[Platform], width: int):
        """Updates physics and handles platform landing/crumble triggers."""
        # Horizontal Movement
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += SPEED

        # Jump Input
        if (
            keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # Apply Gravity
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        prev_bottom = self.rect.bottom

        # Apply Movement
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        self.rect.y += int(self.vel_y)

        self.on_ground = False
        for p in platforms:
            # Ignore platforms that have disintegrated
            if p.destroyed:
                continue

            # Landing condition
            if (
                self.vel_y > 0
                and prev_bottom <= p.rect.top
                and self.rect.bottom >= p.rect.top
                and self.rect.right > p.rect.left
                and self.rect.left < p.rect.right
            ):
                self.rect.bottom = p.rect.top
                self.on_ground = True

                # Trigger landing effect (starts crumbling timer if applicable)
                bounce_vel = p.trigger_land()
                self.vel_y = 0
                break

    def draw(self, screen: pygame.Surface, cam_y: float):
        """Draws player avatar relative to camera position."""
        dr = self.rect.move(0, -int(cam_y))
        pygame.draw.rect(screen, self.color, dr, border_radius=6)
        pygame.draw.circle(screen, (255, 220, 180), (dr.centerx, dr.top + 8), 7)