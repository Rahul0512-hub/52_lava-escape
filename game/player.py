import pygame

SPEED = 4
GRAVITY = 0.55
MAX_FALL_SPEED = 12
JUMP_STRENGTH = -13


class Player:
    """Represents the player avatar with jump physics and platform collisions."""

    def __init__(self, x: float, y: float):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0.0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms: list[pygame.Rect], width: int):
        """Updates player position and resolves one-way platform landings.

        Args:
            keys: Pygame key state array.
            platforms: List of platform Pygame Rect objects.
            width: Game window width for edge boundary clamping.
        """
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

        # Store bottom edge position BEFORE applying vertical movement
        prev_bottom = self.rect.bottom

        # Apply Displacement
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        self.rect.y += int(self.vel_y)

        # Reset ground state prior to collision detection
        self.on_ground = False

        # Landing Condition:
        # 1. Player is moving downward (vel_y > 0).
        # 2. Player was above or at platform surface before moving (prev_bottom <= p.top).
        # 3. Player's feet overlap or cross below platform surface (self.rect.bottom >= p.top).
        # 4. Player horizontally overlaps the platform.
        for p in platforms:
            if (
                self.vel_y > 0
                and prev_bottom <= p.top
                and self.rect.bottom >= p.top
                and self.rect.right > p.left
                and self.rect.left < p.right
            ):
                self.rect.bottom = p.top
                self.vel_y = 0
                self.on_ground = True
                break

    def draw(self, screen: pygame.Surface, cam_y: float):
        """Draws player avatar relative to camera position."""
        dr = self.rect.move(0, -int(cam_y))
        pygame.draw.rect(screen, self.color, dr, border_radius=6)
        pygame.draw.circle(screen, (255, 220, 180), (dr.centerx, dr.top + 8), 7)