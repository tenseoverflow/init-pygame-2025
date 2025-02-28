import pygame
import random
import time
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()
from game_screen import screen
from resources import *
from button import *
from fruit import *

# Screen settings
pygame.display.set_caption("Fruit Ninja")
icon = pygame.image.load("assets/icon.png").convert_alpha()
pygame.display.set_icon(icon)

# Clock
clock = pygame.time.Clock()

game_over_overlay = pygame.Surface(
    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()  # Creating a surface with supports transparency
game_over_overlay.fill(pygame.Color(0, 0, 0, 127))


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
        sounds["flute"].play()
        sounds["ambience"].play(-1)
        self.state = STATE_PLAYING

    def to_main_menu(self):
        pygame.mixer.stop()
        sounds["soundtrack"].play(-1)
        self.score = 0
        self.lives = 3
        self.state = STATE_MENU

    def restart_game(self):
        pygame.mixer.stop()
        sounds["flute"].play()
        sounds["ambience"].play(-1)
        self.score = 0
        self.lives = 3
        self.state = STATE_PLAYING

    def quit_game(self):
        pygame.quit()
        exit()

    def spawn_fruit(self):
        fruit_type = random.choice(list(fruit_images.keys()))
        x = random.randint(150, SCREEN_WIDTH - 150)
        y = SCREEN_HEIGHT
        trajectory = (random.choice([-2, 2]), random.randint(-20, -18))
        self.fruits.append(Fruit(fruit_type, x, y, trajectory))
        if fruit_type == "bomb":
            sounds["bomb_throw"].play()
        else:
            sounds["throw"].play()

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
        for fruit in self.fruits.copy():
            if fruit.hitbox.collidepoint(mouse_pos) and not fruit.sliced:
                fruit.slice()
                if fruit.type == "bomb":
                    sounds["kaboom"].play()
                    self.lives = 0
                    self.state = STATE_GAME_OVER
                    self.fruits.clear()
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

        for fruit in self.fruits.copy():
            if fruit.y > SCREEN_HEIGHT and not fruit.sliced:
                if fruit.type != "bomb":
                    self.lives -= 1
                    sounds["miss"].play()
                self.fruits.remove(fruit)

        if self.lives <= 0:
            self.state = STATE_GAME_OVER
            self.fruits.clear()

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
