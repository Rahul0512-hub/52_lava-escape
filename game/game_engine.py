import pygame
from game.player import Player
from game.world import generate_platforms, draw_lava

WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)

# Position ground near bottom so starting platform is visible immediately
GROUND_Y = HEIGHT - 60


class GameEngine:
    """Core engine managing game loop, states, rendering, and HUD overlays."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 18, bold=True)
        self.reset()

    def reset(self):
        self.platforms = generate_platforms(WIDTH, GROUND_Y)
        self.player = Player(WIDTH // 2 - 16, GROUND_Y - 50)
        self.cam_y = 0
        self.lava_y = GROUND_Y + 120  # Delay lava start to allow setup jump
        self.base_lava_rise = 0.4
        self.lava_rise = 0.4
        self.surge_timer = 0
        self.surge_duration = 0
        self.score = 0
        self.game_over = False
        self.won = False
        self.top_y = self.platforms[-1].rect.y
        self.frame = 0
        self.time_survived = 0.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, WIDTH)

        # Update platform states (handles crumbling timer)
        for p in self.platforms:
            p.update()

        # Update height and time metrics
        self.frame += 1
        self.time_survived = self.frame / FPS
        self.score = max(0, (GROUND_Y - self.player.rect.y) // 10)

        # Camera tracks upward only (locks when player falls downward)
        target = self.player.rect.centery - HEIGHT // 2
        if target < self.cam_y:
            self.cam_y = target

        # Base speed acceleration and periodic lava surges
        self.base_lava_rise = min(1.2, self.base_lava_rise + 0.0003)
        self.surge_timer += 1

        if self.surge_timer > 300:  # Trigger surge every ~5 seconds
            self.surge_duration = 90
            self.surge_timer = 0

        if self.surge_duration > 0:
            self.lava_rise = self.base_lava_rise * 2.5
            self.surge_duration -= 1
        else:
            self.lava_rise = self.base_lava_rise

        self.lava_y -= self.lava_rise

        # Defeat condition: Trigger only when player contacts rising lava surface
        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True

        # Victory condition
        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)

        # Draw world entities
        for p in self.platforms:
            p.draw(self.screen, self.cam_y)

        self.player.draw(self.screen, self.cam_y)
        draw_lava(self.screen, self.lava_y, self.cam_y, WIDTH, HEIGHT, self.frame)

        # Render HUD Panel
        self._draw_hud()

        # Render score card upon game completion
        if self.game_over:
            self._msg("LAVA GOT YOU!", (230, 70, 70))
        elif self.won:
            self._msg("ESCAPED!", (80, 220, 100))

        pygame.display.flip()

    def _draw_hud(self):
        """Renders top status bar for player height, lava speed, and time."""
        hud_bg = pygame.Surface((WIDTH - 20, 42), pygame.SRCALPHA)
        hud_bg.fill((10, 10, 20, 180))
        self.screen.blit(hud_bg, (10, 10))
        pygame.draw.rect(
            self.screen, (70, 70, 100), (10, 10, WIDTH - 20, 42), width=1, border_radius=4
        )

        txt_height = self.font.render(f"HEIGHT: {self.score}m", True, (255, 220, 100))
        txt_speed = self.font.render(f"LAVA: {self.lava_rise:.2f}x", True, (255, 120, 80))
        txt_time = self.font.render(f"TIME: {self.time_survived:.1f}s", True, (200, 220, 255))

        self.screen.blit(txt_height, (24, 22))
        self.screen.blit(txt_speed, (180, 22))
        self.screen.blit(txt_time, (340, 22))

        # Lava surge warning banner
        if self.surge_duration > 0 and not (self.game_over or self.won):
            surge_box = pygame.Surface((240, 26), pygame.SRCALPHA)
            surge_box.fill((200, 30, 30, 200))
            self.screen.blit(surge_box, (WIDTH // 2 - 120, 58))
            surge_txt = self.font.render("! LAVA SURGE WARNING !", True, (255, 255, 255))
            self.screen.blit(surge_txt, (WIDTH // 2 - surge_txt.get_width() // 2, 63))

    def _msg(self, title: str, color: tuple):
        """Displays game over / victory score summary overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        card = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 - 130, 340, 260)
        pygame.draw.rect(self.screen, (25, 25, 40), card, border_radius=12)
        pygame.draw.rect(self.screen, color, card, width=2, border_radius=12)

        title_surf = self.big_font.render(title, True, color)
        self.screen.blit(title_surf, (card.centerx - title_surf.get_width() // 2, card.top + 20))

        metrics = [
            f"Final Height : {self.score} m",
            f"Time Survived: {self.time_survived:.1f} s",
            f"Max Lava Speed: {self.lava_rise:.2f} x",
        ]

        for idx, line in enumerate(metrics):
            txt = self.sub_font.render(line, True, (220, 220, 220))
            self.screen.blit(txt, (card.left + 35, card.top + 80 + idx * 30))

        restart_txt = self.font.render("Press 'R' to Restart", True, (255, 220, 100))
        self.screen.blit(
            restart_txt, (card.centerx - restart_txt.get_width() // 2, card.bottom - 35)
        )

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()