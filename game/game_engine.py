import pygame
from game.player import Player
from game.world import generate_platforms, draw_lava

WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)
GROUND_Y = HEIGHT + 200


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 42, bold=True)
        self.reset()

    def reset(self):
        self.platforms = generate_platforms(WIDTH, GROUND_Y)
        self.player = Player(WIDTH // 2 - 16, GROUND_Y - 50)
        self.cam_y = 0
        self.lava_y = GROUND_Y + 60
        self.base_lava_rise = 0.4
        self.lava_rise = 0.4
        self.surge_timer = 0
        self.surge_duration = 0
        self.score = 0
        self.game_over = False
        self.won = False
        self.top_y = self.platforms[-1].rect.y
        self.frame = 0

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

        # Update platforms (crumbling timers)
        for p in self.platforms:
            p.update()

        # Smooth camera tracking
        target = self.player.rect.centery - HEIGHT // 2
        if target < self.cam_y:
            self.cam_y = target

        # --- Task 4: Base Lava Speed & Periodic Surge Logic ---
        self.base_lava_rise = min(1.2, self.base_lava_rise + 0.0003)
        self.surge_timer += 1

        # Trigger surge phase every ~5 seconds (300 frames) for ~1.5 seconds (90 frames)
        if self.surge_timer > 300:
            self.surge_duration = 90
            self.surge_timer = 0

        if self.surge_duration > 0:
            self.lava_rise = self.base_lava_rise * 2.5  # 2.5x speed surge multiplier
            self.surge_duration -= 1
        else:
            self.lava_rise = self.base_lava_rise

        self.lava_y -= self.lava_rise
        self.score = max(0, (GROUND_Y - self.player.rect.y) // 10)
        self.frame += 1

        # Check Game Over / Victory
        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True
        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)

        # Draw Platforms
        for p in self.platforms:
            p.draw(self.screen, self.cam_y)

        # Draw Player & Lava
        self.player.draw(self.screen, self.cam_y)
        draw_lava(self.screen, self.lava_y, self.cam_y, WIDTH, HEIGHT, self.frame)

        # --- Task 4: Real-Time Danger Meter HUD ---
        sc = self.font.render(
            f"Height: {self.score}m  Lava Speed: {self.lava_rise:.2f}x",
            True,
            (220, 200, 180),
        )
        self.screen.blit(sc, (8, 10))

        # Flashing Lava Surge Warning Banner
        if self.surge_duration > 0:
            surge_txt = self.font.render("! LAVA SURGE WARNING !", True, (255, 60, 60))
            self.screen.blit(surge_txt, (WIDTH // 2 - surge_txt.get_width() // 2, 35))

        # Message Overlay
        if self.game_over:
            self._msg("LAVA GOT YOU!", (220, 80, 40))
        if self.won:
            self._msg("ESCAPED!", (80, 220, 100))

        pygame.display.flip()

    def _msg(self, text: str, color: tuple):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))
        m = self.big_font.render(text, True, color)
        s = self.font.render("Press R to Play Again", True, (200, 200, 200))
        self.screen.blit(m, (WIDTH // 2 - m.get_width() // 2, HEIGHT // 2 - 40))
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 20))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()