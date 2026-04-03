import pygame
import sys
import random
import math
import numpy as np

pygame.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

BLACK = (0, 0, 0)
BLUE = (0, 0, 215)
RED = (215, 0, 0)
MAGENTA = (215, 0, 215)
GREEN = (0, 215, 0)
CYAN = (0, 215, 215)
YELLOW = (215, 215, 0)
WHITE = (215, 215, 215)
BRIGHT_BLUE = (0, 0, 255)
BRIGHT_RED = (255, 0, 0)
BRIGHT_MAGENTA = (255, 0, 255)
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_CYAN = (0, 255, 255)
BRIGHT_YELLOW = (255, 255, 0)
BRIGHT_WHITE = (255, 255, 255)

BRICK_COLORS = [
    BRIGHT_RED, BRIGHT_MAGENTA, BRIGHT_YELLOW, BRIGHT_GREEN,
    BRIGHT_CYAN, BRIGHT_BLUE, RED, MAGENTA, YELLOW, GREEN
]

PADDLE_WIDTH = 80
PADDLE_HEIGHT = 12
PADDLE_SPEED = 7
PADDLE_Y = SCREEN_HEIGHT - 40

BALL_SIZE = 8
BALL_SPEED_INITIAL = 4.0
BALL_SPEED_INCREMENT = 0.2
BALL_MAX_SPEED = 8.0

BRICK_ROWS = 10
BRICK_COLS = 12
BRICK_WIDTH = 48
BRICK_HEIGHT = 16
BRICK_PADDING = 2
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))) // 2

BORDER_THICKNESS = 8


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = float(SCREEN_WIDTH // 2)
        self.y = float(PADDLE_Y - 20)
        angle = random.uniform(-60, 60)
        angle_rad = math.radians(angle - 90)
        self.dx = BALL_SPEED_INITIAL * math.sin(angle_rad)
        self.dy = -BALL_SPEED_INITIAL * math.cos(angle_rad)
        if abs(self.dy) < 1.0:
            self.dy = -BALL_SPEED_INITIAL * 0.7
        self.speed = BALL_SPEED_INITIAL
        self.active = False

    def launch(self):
        self.active = True

    def update(self):
        if not self.active:
            return None
        self.x += self.dx
        self.y += self.dy
        if self.x - BALL_SIZE // 2 <= BORDER_THICKNESS:
            self.x = BORDER_THICKNESS + BALL_SIZE // 2
            self.dx = abs(self.dx)
            return "wall"
        if self.x + BALL_SIZE // 2 >= SCREEN_WIDTH - BORDER_THICKNESS:
            self.x = SCREEN_WIDTH - BORDER_THICKNESS - BALL_SIZE // 2
            self.dx = -abs(self.dx)
            return "wall"
        if self.y - BALL_SIZE // 2 <= BORDER_THICKNESS:
            self.y = BORDER_THICKNESS + BALL_SIZE // 2
            self.dy = abs(self.dy)
            return "wall"
        if self.y + BALL_SIZE // 2 >= SCREEN_HEIGHT:
            return "lost"
        return None

    def increase_speed(self):
        self.speed = min(self.speed + BALL_SPEED_INCREMENT, BALL_MAX_SPEED)
        current_speed = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if current_speed > 0:
            factor = self.speed / current_speed
            self.dx *= factor
            self.dy *= factor

    def draw(self, surface):
        pygame.draw.rect(surface, BRIGHT_WHITE,
                         (int(self.x - BALL_SIZE // 2),
                          int(self.y - BALL_SIZE // 2),
                          BALL_SIZE, BALL_SIZE))


class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = PADDLE_Y

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += PADDLE_SPEED
        self.x = max(BORDER_THICKNESS,
                     min(self.x, SCREEN_WIDTH - BORDER_THICKNESS - self.width))

    def draw(self, surface):
        pygame.draw.rect(surface, BRIGHT_WHITE,
                         (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, WHITE,
                         (self.x + 2, self.y + 2,
                          self.width - 4, self.height - 4))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Brick:
    def __init__(self, x, y, color, points):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.points = points
        self.alive = True

    def draw(self, surface):
        if not self.alive:
            return
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height))
        darker = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.rect(surface, darker,
                         (self.x, self.y, self.width, self.height), 1)
        lighter = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.line(surface, lighter,
                         (self.x + 1, self.y + 1),
                         (self.x + self.width - 2, self.y + 1))
        pygame.draw.line(surface, lighter,
                         (self.x + 1, self.y + 1),
                         (self.x + 1, self.y + self.height - 2))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.life = random.randint(10, 30)
        self.max_life = self.life

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            color = tuple(int(c * alpha) for c in self.color)
            size = max(1, int(3 * alpha))
            pygame.draw.rect(surface, color,
                             (int(self.x), int(self.y), size, size))


def generate_square_wave(freq, duration, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * freq * t))
    wave = (wave * 16000).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return stereo


def generate_sweep_tone(start_freq, end_freq, duration, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    freq = np.linspace(start_freq, end_freq, n_samples)
    phase = np.cumsum(freq / sample_rate) * 2 * np.pi
    wave = np.sign(np.sin(phase))
    envelope = np.linspace(1.0, 0.0, n_samples)
    wave = (wave * envelope * 16000).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return stereo


def create_sounds():
    sounds = {}
    try:
        sounds['paddle'] = pygame.mixer.Sound(
            buffer=generate_square_wave(880, 0.05))
        sounds['brick'] = pygame.mixer.Sound(
            buffer=generate_square_wave(440, 0.05))
        sounds['wall'] = pygame.mixer.Sound(
            buffer=generate_square_wave(220, 0.03))
        sounds['lose'] = pygame.mixer.Sound(
            buffer=generate_sweep_tone(400, 100, 0.3))
        sounds['level'] = pygame.mixer.Sound(
            buffer=generate_sweep_tone(300, 900, 0.5))
        for s in sounds.values():
            s.set_volume(0.3)
    except Exception:
        pass
    return sounds


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("WALL - ZX Spectrum")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.sounds = create_sounds()
        self.state = "title"
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.level = 1
        self.bricks = []
        self.particles = []
        self.paddle = Paddle()
        self.ball = Ball()
        self.title_timer = 0
        self.border_color = BRIGHT_BLUE
        self.screen_flash = 0
        self.lose_timer = 0

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def create_bricks(self):
        self.bricks = []
        for row in range(BRICK_ROWS):
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            points = (BRICK_ROWS - row) * 10
            for col in range(BRICK_COLS):
                x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
                y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
                self.bricks.append(Brick(x, y, color, points))

    def spawn_particles(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.particles = []
        self.paddle = Paddle()
        self.ball = Ball()
        self.create_bricks()

    def check_paddle_collision(self):
        ball_rect = pygame.Rect(
            self.ball.x - BALL_SIZE // 2,
            self.ball.y - BALL_SIZE // 2,
            BALL_SIZE, BALL_SIZE)
        paddle_rect = self.paddle.get_rect()
        if ball_rect.colliderect(paddle_rect) and self.ball.dy > 0:
            hit_pos = (self.ball.x - (self.paddle.x + self.paddle.width / 2))
            hit_pos /= (self.paddle.width / 2)
            hit_pos = max(-1, min(1, hit_pos))
            angle = hit_pos * 60
            angle_rad = math.radians(angle)
            speed = math.sqrt(self.ball.dx ** 2 + self.ball.dy ** 2)
            self.ball.dx = speed * math.sin(angle_rad)
            self.ball.dy = -speed * math.cos(angle_rad)
            self.ball.y = self.paddle.y - BALL_SIZE // 2 - 1
            self.play_sound('paddle')
            return True
        return False

    def check_brick_collisions(self):
        ball_rect = pygame.Rect(
            self.ball.x - BALL_SIZE // 2,
            self.ball.y - BALL_SIZE // 2,
            BALL_SIZE, BALL_SIZE)
        for brick in self.bricks:
            if not brick.alive:
                continue
            brick_rect = brick.get_rect()
            if ball_rect.colliderect(brick_rect):
                brick.alive = False
                self.score += brick.points
                if self.score > self.high_score:
                    self.high_score = self.score
                dx = self.ball.x - (brick.x + brick.width / 2)
                dy = self.ball.y - (brick.y + brick.height / 2)
                if abs(dx / brick.width) > abs(dy / brick.height):
                    self.ball.dx = -self.ball.dx
                else:
                    self.ball.dy = -self.ball.dy
                self.spawn_particles(
                    brick.x + brick.width // 2,
                    brick.y + brick.height // 2,
                    brick.color)
                self.ball.increase_speed()
                self.play_sound('brick')
                self.screen_flash = 3
                return True
        return False

    def all_bricks_destroyed(self):
        return all(not brick.alive for brick in self.bricks)

    def draw_border(self):
        color = self.border_color
        pygame.draw.rect(self.screen, color,
                         (0, 0, SCREEN_WIDTH, BORDER_THICKNESS))
        pygame.draw.rect(self.screen, color,
                         (0, 0, BORDER_THICKNESS, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, color,
                         (SCREEN_WIDTH - BORDER_THICKNESS, 0,
                          BORDER_THICKNESS, SCREEN_HEIGHT))
    def draw_hud(self):
        score_text = self.font_small.render(
            f"SCORE: {self.score}", True, BRIGHT_YELLOW)
        self.screen.blit(score_text, (BORDER_THICKNESS + 10, SCREEN_HEIGHT - 25))

        hi_text = self.font_small.render(
            f"HI: {self.high_score}", True, BRIGHT_GREEN)
        self.screen.blit(hi_text, (SCREEN_WIDTH // 2 - hi_text.get_width() // 2,
                                   SCREEN_HEIGHT - 25))

        lives_text = self.font_small.render(
            f"LIVES: {self.lives}", True, BRIGHT_RED)
        self.screen.blit(lives_text,
                         (SCREEN_WIDTH - BORDER_THICKNESS - lives_text.get_width() - 10,
                          SCREEN_HEIGHT - 25))

        level_text = self.font_small.render(
            f"LEVEL: {self.level}", True, BRIGHT_CYAN)
        self.screen.blit(level_text,
                         (SCREEN_WIDTH // 2 - level_text.get_width() // 2,
                          BORDER_THICKNESS + 5))

    def draw_title_screen(self):
        self.title_timer += 1

        # Animated background stripes
        for i in range(0, SCREEN_HEIGHT, 20):
            color_idx = (i // 20 + self.title_timer // 10) % len(BRICK_COLORS)
            alpha = 40
            stripe_color = tuple(max(0, c - 200) for c in BRICK_COLORS[color_idx])
            pygame.draw.rect(self.screen, stripe_color,
                             (0, i, SCREEN_WIDTH, 10))

        # Title
        title_y = 120 + int(math.sin(self.title_timer * 0.05) * 10)
        title = self.font_large.render("W A L L", True, BRIGHT_WHITE)
        shadow = self.font_large.render("W A L L", True, BLUE)
        self.screen.blit(shadow,
                         (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3,
                          title_y + 3))
        self.screen.blit(title,
                         (SCREEN_WIDTH // 2 - title.get_width() // 2, title_y))

        # Subtitle
        sub = self.font_medium.render("ZX Spectrum Edition", True, BRIGHT_CYAN)
        self.screen.blit(sub,
                         (SCREEN_WIDTH // 2 - sub.get_width() // 2, title_y + 60))

        # Flashing prompt
        if (self.title_timer // 30) % 2 == 0:
            prompt = self.font_medium.render("Press SPACE to Start", True, BRIGHT_YELLOW)
            self.screen.blit(prompt,
                             (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 300))

        # Controls info
        ctrl1 = self.font_small.render("LEFT/RIGHT or A/D to move paddle", True, WHITE)
        ctrl2 = self.font_small.render("SPACE to launch ball", True, WHITE)
        ctrl3 = self.font_small.render("ESC to quit", True, WHITE)
        self.screen.blit(ctrl1, (SCREEN_WIDTH // 2 - ctrl1.get_width() // 2, 370))
        self.screen.blit(ctrl2, (SCREEN_WIDTH // 2 - ctrl2.get_width() // 2, 395))
        self.screen.blit(ctrl3, (SCREEN_WIDTH // 2 - ctrl3.get_width() // 2, 420))

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        go_text = self.font_large.render("GAME OVER", True, BRIGHT_RED)
        self.screen.blit(go_text,
                         (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 160))

        score_text = self.font_medium.render(
            f"Final Score: {self.score}", True, BRIGHT_YELLOW)
        self.screen.blit(score_text,
                         (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 230))

        hi_text = self.font_medium.render(
            f"High Score: {self.high_score}", True, BRIGHT_GREEN)
        self.screen.blit(hi_text,
                         (SCREEN_WIDTH // 2 - hi_text.get_width() // 2, 270))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            restart = self.font_medium.render(
                "Press SPACE to Play Again", True, BRIGHT_WHITE)
            self.screen.blit(restart,
                             (SCREEN_WIDTH // 2 - restart.get_width() // 2, 340))

    def draw_level_complete_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render(
            f"LEVEL {self.level} COMPLETE!", True, BRIGHT_GREEN)
        self.screen.blit(text,
                         (SCREEN_WIDTH // 2 - text.get_width() // 2, 180))

        score_text = self.font_medium.render(
            f"Score: {self.score}", True, BRIGHT_YELLOW)
        self.screen.blit(score_text,
                         (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cont = self.font_medium.render(
                "Press SPACE to Continue", True, BRIGHT_WHITE)
            self.screen.blit(cont,
                             (SCREEN_WIDTH // 2 - cont.get_width() // 2, 320))

    def update_particles(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw_particles(self):
        for p in self.particles:
            p.draw(self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state == "title":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = "playing"

                elif self.state == "playing":
                    if event.key == pygame.K_SPACE and not self.ball.active:
                        self.ball.launch()

                elif self.state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.state = "title"

                elif self.state == "level_complete":
                    if event.key == pygame.K_SPACE:
                        self.level += 1
                        self.create_bricks()
                        self.ball.reset()
                        self.paddle = Paddle()
                        self.state = "playing"

        return True

    def update(self):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        self.paddle.update(keys)

        # Ball follows paddle before launch
        if not self.ball.active:
            self.ball.x = self.paddle.x + self.paddle.width / 2
            self.ball.y = self.paddle.y - BALL_SIZE // 2 - 1
            return

        result = self.ball.update()

        if result == "wall":
            self.play_sound('wall')
        elif result == "lost":
            self.lives -= 1
            self.play_sound('lose')
            if self.lives <= 0:
                self.state = "game_over"
            else:
                self.ball.reset()
                self.paddle = Paddle()

        self.check_paddle_collision()
        self.check_brick_collisions()

        if self.all_bricks_destroyed():
            self.play_sound('level')
            self.state = "level_complete"

        self.update_particles()

        # Screen flash decay
        if self.screen_flash > 0:
            self.screen_flash -= 1

        # Border color cycling
        self.border_color = BRICK_COLORS[
            (pygame.time.get_ticks() // 500) % len(BRICK_COLORS)]

    def draw(self):
        # Background
        if self.screen_flash > 0:
            self.screen.fill((30, 30, 60))
        else:
            self.screen.fill(BLACK)

        if self.state == "title":
            self.draw_title_screen()
        elif self.state == "playing":
            self.draw_border()
            for brick in self.bricks:
                brick.draw(self.screen)
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self.draw_particles()
            self.draw_hud()
        elif self.state == "game_over":
            self.draw_border()
            for brick in self.bricks:
                brick.draw(self.screen)
            self.paddle.draw(self.screen)
            self.draw_particles()
            self.draw_hud()
            self.draw_game_over_screen()
        elif self.state == "level_complete":
            self.draw_border()
            self.paddle.draw(self.screen)
            self.draw_particles()
            self.draw_hud()
            self.draw_level_complete_screen()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
