import pygame
import random

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
RED = (255, 0, 0)

# Clock and font
clock = pygame.time.Clock()
big_font = pygame.font.Font('assets/fonts/gamecamper.ttf', 36)
font = pygame.font.Font('assets/fonts/gamecamper-lite.ttf', 24)

# Load assets
backgrounds = [pygame.image.load(
    f"assets/background{i}.png") for i in range(1, 3)]
fruit_images = {
    "apple": pygame.image.load("assets/fruits/apple.png"),
    "banana": pygame.image.load("assets/fruits/banana.png"),
    "bomb": pygame.image.load("assets/fruits/bomb.png"),
    "melon": pygame.image.load("assets/fruits/melon.png"),
    "orange": pygame.image.load("assets/fruits/orange.png"),
}

# Placeholder for sliced GIFs
gif_frames = {"apple": [], "banana": [],
              "bomb": [], "melon": [], "orange": [], }

# Classes


class Fruit:
    def __init__(self, fruit_type, x, y, trajectory):
        self.type = fruit_type
        self.image = fruit_images[fruit_type]
        self.x = x
        self.y = y
        self.trajectory = trajectory  # A tuple (x_speed, y_speed)
        self.hitbox = self.image.get_rect(topleft=(self.x, self.y))
        self.sliced = False

    def move(self):
        self.x += self.trajectory[0]
        self.y += self.trajectory[1]
        self.hitbox.topleft = (self.x, self.y)

    def draw(self, surface):
        if not self.sliced:
            surface.blit(self.image, (self.x, self.y))

    def slice(self):
        self.sliced = True
        # Play GIF (placeholder for now)


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
        for fruit in self.fruits:
            if fruit.hitbox.collidepoint(mouse_pos) and not fruit.sliced:
                fruit.slice()
                if fruit.type == "bomb":
                    self.lives -= 1
                    # Play bomb effect
                else:
                    self.score += 10 if fruit.type == "apple" else 20
                if self.score > self.highscore:
                    self.highscore = self.score

    def update(self):
        if random.randint(1, 50) == 1:  # Spawn fruit occasionally
            self.spawn_fruit()

        for fruit in self.fruits:
            fruit.move()
            if fruit.y > SCREEN_HEIGHT and not fruit.sliced:
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
        highscore_text = font.render(
            f"Best: {self.highscore}", True, YELLOW)
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
