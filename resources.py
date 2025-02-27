"""This file holds all images and sounds for the Fruit Ninja game."""
from constants import *
import pygame
import os
from PIL import Image

# Load images
# Here's some examples how images can be loaded using PyGame.
# background_img = pygame.image.load("images/background.png")
# pipe_img = pygame.image.load("images/pipe.png")
# score_img = pygame.image.load("images/score.png")
# logo_img = pygame.image.load("images/logo.png")
# instructions_img = pygame.image.load("images/instructions.png")

# Now's your turn! Load the image for the bird (bird_img).



# Load sound effects
# Here's an example how sounds can be loaded using PyGame.
# flap_sound = pygame.mixer.Sound("sounds/flap.wav")

# But our game needs more sounds! Add sound effects for:
# the bird colliding with the pipe (hurt_sound), and
# a score increase (point_sound).

big_font = pygame.font.Font('assets/fonts/gamecamper.ttf', 36)
font = pygame.font.Font('assets/fonts/gamecamper-lite.ttf', 24)

# Load fruit iamages
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
            image = pygame.image.load(os.path.join(directory, filename))
            pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            backgrounds[background_name] = image
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

# Load sounds
sounds = load_sounds("assets/sounds")
