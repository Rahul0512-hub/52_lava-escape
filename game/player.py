import pygame

# Movement constants
SPEED = 4
GRAVITY = 0.55
MAX_FALL_SPEED = 12
JUMP_STRENGTH = -13


class Player:
    """Represents the playable character with platformer physics and collision logic."""

    def __init__(self, x: float, y: float):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0.0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms: list[pygame.Rect], width: int):
        """Updates player position, applies physics, and handles platform collisions.

        Args:
            keys: Pygame key state array.
            platforms: List of platform Pygame Rects.
            width: Game window width for boundary clamping.
        """
        # --- Horizontal Input ---
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += SPEED

        # --- Jump Input ---
        if (
            keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # --- Apply Gravity ---
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # Track player's bottom edge position before vertical movement
        prev_bottom = self.rect.bottom

        # --- Apply Movement ---
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        self.rect.y += int(self.vel_y)

        # --- Platform Collisions ---
        self.on_ground = False

        # Landing condition:
        # 1. Player is descending (vel_y > 0).
        # 2. Before vertical movement, player's feet were at or above the platform's top surface.
        # 3. After vertical movement, player's feet overlap or cross below the platform's top surface.
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
                break  # Land on the highest valid platform in range

    def draw(self, screen: pygame.Surface, cam_y: float):
        """Draws the player relative to camera position."""
        dr = self.rect.move(0, -int(cam_y))
        pygame.draw.rect(screen, self.color, dr, border_radius=6)
        pygame.draw.circle(screen, (255, 220, 180), (dr.centerx, dr.top + 8), 7)