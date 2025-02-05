import pygame
import random
from PIL import Image
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Fruit Ninja")
icon = pygame.image.load("assets/icon.png").convert_alpha()
pygame.display.set_icon(icon)

# Colors
YELLOW = (253, 231, 56)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock and font
clock = pygame.time.Clock()
big_font = pygame.font.Font('assets/fonts/gamecamper.ttf', 36)
font = pygame.font.Font('assets/fonts/gamecamper-lite.ttf', 24)

# Load fruit images as frame sequences
def load_gif_frames(path):
    pil_img = Image.open(path)
    frames = []
    try:
        while True:
            frame = pil_img.convert("RGBA")
            frames.append(pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA"))
            pil_img.seek(len(frames))
    except EOFError:
        pass
    return frames

fruit_images = {
    "apple": load_gif_frames("assets/fruits/apple.gif"),
    "banana": load_gif_frames("assets/fruits/banana.gif"),
    "bomb": load_gif_frames("assets/fruits/bomb.gif"),
    "melon": load_gif_frames("assets/fruits/melon.gif"),
    "orange": load_gif_frames("assets/fruits/orange.gif"),
}
kaboom_frames = load_gif_frames("assets/kaboom.gif")

# Load backgrounds
backgrounds = {"Dojo": pygame.image.load("assets/background_dojo.png"),
               "Peace": pygame.image.load("assets/background_peace.png"),
               "Basic": pygame.image.load("assets/background_basic.png")}

# Game States
STATE_MENU = "menu"
STATE_MAP_SELECTION = "map_selection"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, font, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.action = action  # Function to call when clicked

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action()

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
        self.state = STATE_MENU
        self.selected_map = "Dojo"
        self.fruits = []
        self.score = 0
        self.lives = 3
        self.mouse_held = False
        self.highscore = self.load_highscore()
        self.create_buttons()

    def create_buttons(self):
        self.buttons = [
            Button("Start Game", 540, 300, 200, 50, YELLOW, WHITE, font, self.start_game),
            Button("Settings", 540, 400, 200, 50, YELLOW, WHITE, font, self.settings),
        ]

        self.map_buttons = [
            Button("Dojo", 400, 300, 200, 50, YELLOW, WHITE, font, lambda: self.select_map("Dojo")),
            Button("Peace", 640, 300, 200, 50, YELLOW, WHITE, font, lambda: self.select_map("Peace")),
            Button("Basic", 880, 300, 200, 50, YELLOW, WHITE, font, lambda: self.select_map("Basic")),
        ]

        self.game_over_buttons = [
            Button("Restart", 540, 300, 200, 50, YELLOW, WHITE, font, self.start_game),
            Button("Main Menu", 540, 400, 200, 50, YELLOW, WHITE, font, self.to_main_menu),
            Button("Quit", 540, 500, 200, 50, YELLOW, WHITE, font, self.quit_game),
        ]

    def start_game(self):
        self.state = STATE_MAP_SELECTION

    def select_map(self, map_name):
        self.selected_map = map_name
        self.background = backgrounds[self.selected_map]
        self.state = STATE_PLAYING

    def to_main_menu(self):
        self.state = STATE_MENU
        self.create_buttons()

    def settings(self):
        pass  # Placeholder for settings functionality

    def quit_game(self):
        pygame.quit()
        exit()

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
            self.state = STATE_GAME_OVER

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_MAP_SELECTION:
            self.draw_map_selection()
        elif self.state == STATE_PLAYING:
            screen.blit(backgrounds[self.selected_map], (0, 0))
            for fruit in self.fruits:
                fruit.draw(screen)
            score_text = big_font.render(f"{self.score}", True, YELLOW)
            highscore_text = font.render(f"Best: {self.highscore}", True, YELLOW)
            lives_text = font.render(f"Lives: {self.lives}", True, YELLOW)
            screen.blit(icon, (20, 20))
            screen.blit(score_text, (120, 20))
            screen.blit(highscore_text, (20, 110))
            screen.blit(lives_text, (20, 160))
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()

    def draw_menu(self):
        screen.fill(BLACK)
        title = big_font.render("Fruit Ninja", True, YELLOW)
        screen.blit(title, (540, 200))
        for button in self.buttons:
            button.draw(screen)

    def draw_map_selection(self):
        screen.fill(BLACK)
        title = big_font.render("Pick a Map", True, YELLOW)
        screen.blit(title, (540, 200))
        for button in self.map_buttons:
            button.draw(screen)

    def draw_game_over(self):
        screen.fill(BLACK)
        score_text = big_font.render(f"Score: {self.score}", True, YELLOW)
        highscore_text = font.render(f"Highscore: {self.highscore}", True, YELLOW)
        screen.blit(score_text, (540, 200))
        screen.blit(highscore_text, (540, 250))
        for button in self.game_over_buttons:
            button.draw(screen)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_held = True
                    if self.state == STATE_MENU:
                        for button in self.buttons:
                            button.check_click(event)
                    elif self.state == STATE_MAP_SELECTION:
                        for button in self.map_buttons:
                            button.check_click(event)
                    elif self.state == STATE_GAME_OVER:
                        for button in self.game_over_buttons:
                            button.check_click(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_held = False
                

            if self.state == STATE_MENU:
                self.draw_menu()
            elif self.state == STATE_MAP_SELECTION:
                self.draw_map_selection()
            elif self.state == STATE_GAME_OVER:
                self.draw_game_over()

            if self.mouse_held:
                self.handle_slicing()

            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        self.save_highscore()
        pygame.quit()

# Run game
game = Game()
game.run()
