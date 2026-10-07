import math
import random
import pygame

COLOR_NORMAL = (100, 80, 50)
COLOR_CRUMBLING = (180, 100, 50)
COLOR_SPRING = (50, 180, 100)
LAVA_COLOR = (220, 60, 20)


class Platform:
    """Represents an interactive platform with type-specific behaviors."""

    def __init__(self, rect: pygame.Rect, p_type: str = "normal"):
        self.rect = rect
        self.type = p_type  # "normal", "crumbling", "spring"
        self.stepped_on = False
        self.shake_timer = 0
        self.destroyed = False

    def trigger_land(self) -> float:
        """Triggers state changes when landed on. Returns bounce velocity."""
        self.stepped_on = True
        return -13.0  # Standard jump velocity

    def update(self):
        """Updates crumbling shake timer and disintegration state."""
        if self.type == "crumbling" and self.stepped_on and not self.destroyed:
            self.shake_timer += 1
            if self.shake_timer > 45:  # ~0.75s shake delay before breaking
                self.destroyed = True

    def get_draw_rect(self, cam_y: float) -> pygame.Rect:
        """Calculates rendering rect with shaking offset if crumbling."""
        offset_x = 0
        if self.type == "crumbling" and self.stepped_on and not self.destroyed:
            offset_x = random.randint(-2, 2)
        return self.rect.move(offset_x, -int(cam_y))

    def draw(self, screen: pygame.Surface, cam_y: float):
        """Renders the platform onto the screen if active."""
        if self.destroyed:
            return

        dr = self.get_draw_rect(cam_y)
        color = COLOR_NORMAL
        if self.type == "crumbling":
            color = COLOR_CRUMBLING
        elif self.type == "spring":
            color = COLOR_SPRING

        pygame.draw.rect(screen, color, dr, border_radius=4)


class SpringPlatform(Platform):
    """Platform variant that launches player upward with bonus velocity."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(rect, p_type="spring")

    def trigger_land(self) -> float:
        """Overrides jump velocity to provide high-velocity launch."""
        super().trigger_land()
        return -20.0  # High-velocity spring launch


def generate_platforms(width: int, base_y: int, count: int = 30) -> list[Platform]:
    """Generates guaranteed-reachable ascending platform chain."""
    # Ground platform
    plats = [Platform(pygame.Rect(0, base_y, width, 20), p_type="normal")]
    
    prev_x = width // 2 - 60
    prev_w = 120
    y = base_y - 85

    MAX_JUMP_HEIGHT = 100  # Cap vertical distance to guarantee jump height
    MAX_HORIZONTAL_REACH = 160  # Cap horizontal gap distance

    for _ in range(count):
        w = random.randint(90, 160)

        # Calculate reachable horizontal X bounds relative to the previous platform
        min_x = max(0, prev_x - MAX_HORIZONTAL_REACH)
        max_x = min(width - w, prev_x + prev_w + MAX_HORIZONTAL_REACH - w)

        if min_x > max_x:
            x = random.randint(0, width - w)
        else:
            x = random.randint(min_x, max_x)

        rect = pygame.Rect(x, y, w, 16)

        # Weighted selection for platform types
        p_type = random.choices(
            ["normal", "crumbling", "spring"], weights=[0.60, 0.25, 0.15]
        )[0]

        if p_type == "spring":
            plats.append(SpringPlatform(rect))
        else:
            plats.append(Platform(rect, p_type=p_type))

        # Update tracking for next iteration
        prev_x = x
        prev_w = w
        y -= random.randint(70, MAX_JUMP_HEIGHT)

    return plats


def draw_lava(screen: pygame.Surface, lava_y: float, cam_y: float, width: int, height: int, frame: int):
    """Renders rising lava surface waves and glow overlay."""
    ly = int(lava_y - cam_y)
    if ly < height:
        pts = [(0, ly)]
        for x in range(0, width + 20, 20):
            pts.append((x, ly + int(math.sin(x * 0.08 + frame * 0.1) * 8)))
        pts.append((width, height))
        pts.append((0, height))
        pygame.draw.polygon(screen, LAVA_COLOR, pts)

        s = pygame.Surface((width, 30), pygame.SRCALPHA)
        for i in range(15):
            pygame.draw.line(s, (255, 100, 0, max(0, 60 - i * 4)), (0, i), (width, i), 1)
        screen.blit(s, (0, ly - 15))