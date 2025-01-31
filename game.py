import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fruit Ninja")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Load assets
backgrounds = [pygame.image.load(
    f"images/background{i}.png") for i in range(1, 3)]
fruit_images = {
    "apple": pygame.image.load("images/fruits/apple.png"),
    "banana": pygame.image.load("images/fruits/banana.png"),
    "bomb": pygame.image.load("images/fruits/bomb.png")
}

# Placeholder for sliced GIFs
gif_frames = {"apple": [], "banana": [], "bomb": []}

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
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, RED)
        highscore_text = font.render(
            f"Highscore: {self.highscore}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(highscore_text, (10, 90))

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
