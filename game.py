import pygame
import random
from PIL import Image
import time
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fruit Ninja")
icon = pygame.image.load("assets/icon.png").convert_alpha()
pygame.display.set_icon(icon)

# Colors
PRIMARY = (253, 231, 56)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock and font
clock = pygame.time.Clock()
big_font = pygame.font.Font('assets/fonts/gamecamper.ttf', 36)
font = pygame.font.Font('assets/fonts/gamecamper-lite.ttf', 24)

def load_fruit_images(directory):
    fruit_images = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if filename.endswith(".gif"):
            fruit_name = os.path.splitext(filename)[0]  # Get the name without extension
            fruit_images[fruit_name] = load_gif_frames(file_path)  # Load as GIF
        elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
            fruit_name = os.path.splitext(filename)[0]  # Get the name without extension
            image = pygame.image.load(file_path).convert_alpha()  # Load static image
            # Resize the image to be at most 120x120 while keeping the aspect ratio
            fruit_images[fruit_name] = [resize_image(image)]  # Store resized image
    return fruit_images

# Load fruit images as frame sequences for GIFs
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

# Load background images dynamically
def load_background_images(directory):
    backgrounds = {}
    for filename in os.listdir(directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            background_name = os.path.splitext(filename)[0]  # Get the name without extension
            backgrounds[background_name] = pygame.image.load(os.path.join(directory, filename))
        else:
            print(filename)
    return backgrounds

# Load sounds dynamically
def load_sounds(directory):
    sounds = {}
    for filename in os.listdir(directory):
        if filename.lower().endswith((".mp3", ".wav", ".m4a")):
            sound_name = os.path.splitext(filename)[0]  # Get the name without extension
            sounds[sound_name] = pygame.mixer.Sound(os.path.join(directory, filename))
    return sounds

# Resize an image to be at most 120x120, keeping the aspect ratio
def resize_image(image, max_size=120):
    width, height = image.get_size()
    
    # Calculate the scaling factor
    if width > height:
        new_width = min(width, max_size)
        new_height = int((new_width / width) * height)
    else:
        new_height = min(height, max_size)
        new_width = int((new_height / height) * width)

    # Perform the resizing
    return pygame.transform.scale(image, (new_width, new_height))


# Load fruit and kaboom images
fruit_images = load_fruit_images("assets/fruits")
slice_frames = load_gif_frames("assets/effects/slice.gif")

# Load background images
backgrounds = load_background_images("assets/backgrounds")

sounds = load_sounds("assets/sounds")
game_over_overlay = pygame.Surface( \
    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()  # Creating a surface with supports transparency
game_over_overlay.fill(pygame.Color(0, 0, 0, 127))

# Game States
STATE_MENU = "menu"
STATE_MAP_SELECTION = "map_selection"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

GRAVITY = 0.3

class Button:
    def __init__(self, text, text_color, x, y, color, hover_color, action=None, padding=(20, 10)):
        self.text = text
        self.text_color = text_color
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.last_pressed = False
        self.delay = 0.2

        text_surf = font.render(self.text, True, self.text_color)
        self.text_width = text_surf.get_width()
        self.text_height = text_surf.get_height()

        self.width = self.text_width + padding[0] * 2
        self.height = self.text_height + padding[1] * 2

        self.x = x - self.width // 2
        self.y = y - self.height // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, current_color, self.rect)

        text_surf = font.render(self.text, True, self.text_color)
        text_x = self.rect.centerx - self.text_width // 2
        text_y = self.rect.centery - self.text_height // 2
        screen.blit(text_surf, (text_x, text_y))
        
        if self.rect.collidepoint(mouse_pos) and not click and self.last_pressed and self.action:
            current_time = time.time()
            if current_time - self.last_pressed > self.delay:
                self.action()
                self.last_pressed = current_time
        self.last_pressed = click

class Fruit:
    def __init__(self, fruit_type, x, y, trajectory):
        self.type = fruit_type
        self.frames = fruit_images[fruit_type]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.x = x
        self.y = y
        self.angle = 0
        self.rotate_direction = random.choice(range(-25, 25))
        self.trajectory = trajectory
        self.hitbox = self.image.get_rect(topleft=(self.x, self.y))
        self.sliced = False
        self.last_frame_time = pygame.time.get_ticks()
        self.slice_frames = slice_frames
        self.explosion_index = 0
        self.exploding = False

    def move(self):
        if not self.exploding:
            self.angle += self.rotate_direction
            self.x += self.trajectory[0]
            self.y += self.trajectory[1]
            self.trajectory = (self.trajectory[0], self.trajectory[1] + GRAVITY)
            self.hitbox.topleft = (self.x, self.y)

            if pygame.time.get_ticks() - self.last_frame_time > 50:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.last_frame_time = pygame.time.get_ticks()
        elif self.slice_frames:
            if pygame.time.get_ticks() - self.last_frame_time > 50:
                if self.explosion_index < len(self.slice_frames) - 1:
                    self.explosion_index += 1
                    self.image = self.slice_frames[self.explosion_index]
                    self.last_frame_time = pygame.time.get_ticks()
                else:
                    return False  # Mark for removal
        return True

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center = self.image.get_rect(topleft = (self.x, self.y)).center)

        surface.blit(rotated_image, new_rect)

    def slice(self):
        self.angle = 0
        self.sliced = True
        self.exploding = True
        self.image = self.slice_frames[0]
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

        pygame.mixer.stop()
        sounds["soundtrack"].play(-1)

        self.life_images = [
            pygame.image.load(f"assets/lives/lives_{i}.png").convert_alpha() for i in range(4)
        ]

        self.update_positions()

    def create_buttons(self):
        self.buttons = [
            Button("Start Game", BLACK, 540, 300, PRIMARY, WHITE, self.start_game),
            Button("Quit", BLACK, 540, 400, PRIMARY, WHITE, self.quit_game),
        ]

        self.map_buttons = []
        map_x = 400
        map_y = 300
        button_padding = 140

        for i, map_name in enumerate(backgrounds.keys()):
            button = Button(map_name, BLACK, map_x + i * button_padding, map_y, PRIMARY, WHITE, lambda x=map_name: self.select_map(x))
            self.map_buttons.append(button)

        self.game_over_buttons = [
            Button("Retry", BLACK, 540, 300, PRIMARY, WHITE, self.restart_game),
            Button("Back", BLACK, 540, 500, PRIMARY, WHITE, self.to_main_menu),
        ]

    def start_game(self):
        self.state = STATE_MAP_SELECTION

    def select_map(self, map_name):
        self.selected_map = map_name
        self.background = backgrounds[self.selected_map]
        pygame.mixer.stop()
        sounds["ambience_flute"].play(-1)
        self.state = STATE_PLAYING

    def to_main_menu(self):
        pygame.mixer.stop()
        sounds["soundtrack"].play(-1)
        self.fruits = []
        self.score = 0
        self.lives = 3
        self.state = STATE_MENU
        self.create_buttons()

    def restart_game(self):
        self.fruits = []
        self.score = 0
        self.lives = 3
        self.state = STATE_MAP_SELECTION

    def quit_game(self):
        pygame.quit()
        exit()

    def spawn_fruit(self):
        fruit_type = random.choice(list(fruit_images.keys()))
        x = random.randint(150, SCREEN_WIDTH - 150)
        y = SCREEN_HEIGHT
        trajectory = (random.choice([-2, 2]), random.randint(-20, -18))
        self.fruits.append(Fruit(fruit_type, x, y, trajectory))
        if fruit_type != "bomb":
            sounds["throw"].play()
        else:
            sounds["bomb_throw"].play()

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
                    sounds["kaboom"].play()
                    self.lives = 0
                    self.state = STATE_GAME_OVER
                else:
                    sounds["slice"].play()
                    self.score += 1
                if self.score > self.highscore:
                    self.highscore = self.score


    def update(self):
        difficulty = int(round(69 - (self.score / 5)))
        if (difficulty) != 0 and random.randint(1, difficulty) == 1:
            self.spawn_fruit()

        self.fruits = [fruit for fruit in self.fruits if fruit.move()]

        for fruit in self.fruits[:]:
            if fruit.y > SCREEN_HEIGHT and not fruit.exploding:
                if fruit.type != "bomb":
                    self.lives -= 1
                    sounds["miss"].play()
                self.fruits.remove(fruit)

        if self.lives <= 0:
            self.state = STATE_GAME_OVER

    def update_positions(self):
        self.icon_x = SCREEN_WIDTH * 0.02
        self.icon_y = SCREEN_HEIGHT * 0.04
        self.score_x = SCREEN_WIDTH * 0.1
        self.score_y = SCREEN_HEIGHT * 0.04
        self.highscore_x = SCREEN_WIDTH * 0.02
        self.highscore_y = SCREEN_HEIGHT * 0.16
        self.life_x = SCREEN_WIDTH - self.life_images[self.lives].get_width() - SCREEN_WIDTH * 0.02
        self.life_y = SCREEN_HEIGHT * 0.04

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_MAP_SELECTION:
            self.draw_map_selection()
        elif self.state == STATE_PLAYING:
            screen.blit(backgrounds[self.selected_map], (0, 0))
            for fruit in self.fruits:
                fruit.draw(screen)

            score_text = big_font.render(f"{self.score}", True, PRIMARY)
            screen.blit(icon, (self.icon_x, self.icon_y))
            screen.blit(score_text, (self.score_x, self.score_y))

            if self.load_highscore() > 0:
                highscore_text = font.render(f"BEST: {self.highscore}", True, PRIMARY)
                screen.blit(highscore_text, (self.highscore_x, self.highscore_y))

            life_image = self.life_images[self.lives]
            screen.blit(life_image, (self.life_x, self.life_y))

        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
            self.save_highscore()

    def draw_menu(self):
        screen.blit(backgrounds[self.selected_map], (0, 0))
        screen.blit(game_over_overlay, (0, 0))
        
        title = big_font.render("FRUIT NINJA", True, PRIMARY)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 150))
        
        button_y = 300
        for button in self.buttons:
            button_x = (SCREEN_WIDTH - button.width) // 2
            button.rect.x = button_x
            button.rect.y = button_y
            button.draw(screen)
            button_y += 100

    def draw_map_selection(self):
        screen.blit(backgrounds[self.selected_map], (0, 0))
        screen.blit(game_over_overlay, (0, 0))
        
        title = big_font.render("PICK A MAP", True, PRIMARY)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 150))
        
        button_y = 300
        for button in self.map_buttons:
            button_x = (SCREEN_WIDTH - button.width) // 2
            button.rect.x = button_x
            button.rect.y = button_y
            button.draw(screen)
            button_y += 100

    def draw_game_over(self):
        screen.blit(backgrounds[self.selected_map], (0, 0))
        screen.blit(game_over_overlay, (0, 0))
        
        score_text = big_font.render(f"SCORE: {self.score}", True, PRIMARY)
        score_x = (SCREEN_WIDTH - score_text.get_width()) // 2
        screen.blit(score_text, (score_x, 150))
        
        highscore_text = font.render(f"HIGHSCORE: {self.highscore}", True, PRIMARY)
        highscore_x = (SCREEN_WIDTH - highscore_text.get_width()) // 2
        screen.blit(highscore_text, (highscore_x, 230))

        life_image = self.life_images[self.lives]
        screen.blit(life_image, (self.life_x, self.life_y))
        
        button_y = 300
        for button in self.game_over_buttons:
            button_x = (SCREEN_WIDTH - button.width) // 2
            button.rect.x = button_x
            button.rect.y = button_y
            button.draw(screen)
            button_y += 100


    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_held = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_held = False

            if self.mouse_held:
                self.handle_slicing()
            if self.state == STATE_PLAYING:
                self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        self.save_highscore()
        pygame.quit()

# Run game
game = Game()
game.run()
