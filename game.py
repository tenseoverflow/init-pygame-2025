import pygame
import random
from PIL import Image

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fruit Ninja")
icon = pygame.image.load("assets/icon.png").convert_alpha()
try:
    pygame.display.set_icon(icon)
except NameError:
    pass

# Colors
YELLOW = (253, 231, 56)
BLACK = (0, 0, 0)

# Clock and font
clock = pygame.time.Clock()
big_font = pygame.font.Font('assets/fonts/gamecamper.ttf', 36)
font = pygame.font.Font('assets/fonts/gamecamper-lite.ttf', 24)

# Load backgrounds
backgrounds = [pygame.image.load(
    f"assets/background{i}.png") for i in range(1, 3)]

# Function to load GIF frames


def load_gif_frames(path):
    pil_img = Image.open(path)
    frames = []
    try:
        while True:
            frame = pil_img.convert("RGBA")
            frames.append(pygame.image.fromstring(
                frame.tobytes(), frame.size, "RGBA"))
            pil_img.seek(len(frames))
    except EOFError:
        pass
    return frames


# Load fruit images as frame sequences
fruit_images = {
    "apple": load_gif_frames("assets/fruits/apple.gif"),
    "banana": load_gif_frames("assets/fruits/banana.gif"),
    "bomb": load_gif_frames("assets/fruits/bomb.gif"),
    "melon": load_gif_frames("assets/fruits/melon.gif"),
    "orange": load_gif_frames("assets/fruits/orange.gif"),
}

# Load explosion GIF
kaboom_frames = load_gif_frames("assets/kaboom.gif")


class Fruit:
    def __init__(self, fruit_type, x, y, trajectory):
        self.type = fruit_type
        self.frames = fruit_images[fruit_type]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.x = x
        self.y = y
        self.trajectory = trajectory
        self.hitbox = self.image.get_rect(topleft=(self.x, self.y))
        self.sliced = False
        self.last_frame_time = pygame.time.get_ticks()
        self.explosion_frames = kaboom_frames
        self.explosion_index = 0
        self.exploding = False

    def move(self):
        if not self.exploding:
            self.x += self.trajectory[0]
            self.y += self.trajectory[1]
            self.hitbox.topleft = (self.x, self.y)

            if pygame.time.get_ticks() - self.last_frame_time > 50:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.last_frame_time = pygame.time.get_ticks()
        elif self.explosion_frames:
            if pygame.time.get_ticks() - self.last_frame_time > 50:
                if self.explosion_index < len(self.explosion_frames) - 1:
                    self.explosion_index += 1
                    self.image = self.explosion_frames[self.explosion_index]
                    self.last_frame_time = pygame.time.get_ticks()
                else:
                    return False  # Mark for removal
        return True

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def slice(self):
        self.sliced = True
        self.exploding = True
        self.image = self.explosion_frames[0]
        self.explosion_index = 0
        self.last_frame_time = pygame.time.get_ticks()


class Game:
    def __init__(self):
        self.running = True
        self.background = random.choice(backgrounds)
        self.fruits = []
        self.score = 0
        self.lives = 3
        self.mouse_held = False
        self.highscore = self.load_highscore()

    def spawn_fruit(self):
        fruit_type = random.choice(list(fruit_images.keys()))
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = SCREEN_HEIGHT
        trajectory = (random.choice([-2, 2]), random.randint(-8, -5))
        self.fruits.append(Fruit(fruit_type, x, y, trajectory))

    def load_highscore(self):
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.highscore))

    def handle_slicing(self):
        mouse_pos = pygame.mouse.get_pos()
        for fruit in self.fruits[:]:
            if fruit.hitbox.collidepoint(mouse_pos) and not fruit.sliced:
                fruit.slice()
                if fruit.type == "bomb":
                    self.lives -= 1
                else:
                    self.score += 10 if fruit.type == "apple" else 20
                if self.score > self.highscore:
                    self.highscore = self.score

    def update(self):
        if random.randint(1, 50) == 1:
            self.spawn_fruit()

        self.fruits = [fruit for fruit in self.fruits if fruit.move()]

        for fruit in self.fruits[:]:
            if fruit.y > SCREEN_HEIGHT and not fruit.exploding:
                if fruit.type != "bomb":
                    self.lives -= 1
                self.fruits.remove(fruit)

        if self.lives <= 0:
            self.running = False

    def draw(self):
        screen.blit(self.background, (0, 0))
        for fruit in self.fruits:
            fruit.draw(screen)
        score_text = big_font.render(f"{self.score}", True, YELLOW)
        highscore_text = font.render(f"Best: {self.highscore}", True, YELLOW)
        lives_text = font.render(f"Lives: {self.lives}", True, YELLOW)
        screen.blit(icon, (20, 20))
        screen.blit(score_text, (120, 20))
        screen.blit(highscore_text, (20, 110))
        screen.blit(lives_text, (20, 160))

    def run(self):
        while self.running:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_held = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_held = False

            if self.mouse_held:
                self.handle_slicing()

            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        self.save_highscore()


# Main loop
game = Game()
game.run()

pygame.quit()
