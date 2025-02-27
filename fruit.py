import pygame
from resources import fruit_images, slice_frames
from constants import *
import random

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
        self.slice_frame_count = 0

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
                if self.slice_frame_count < len(self.slice_frames) - 1:
                    self.slice_frame_count += 1
                    self.image = self.slice_frames[self.slice_frame_count]
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
        self.image = self.slice_frames[0]
        self.slice_frame_count = 0
        self.last_frame_time = pygame.time.get_ticks()
