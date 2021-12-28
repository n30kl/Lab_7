from pygame.math import Vector2 as vector
import pygame, random
from helper import *


class Pacman:
    def __init__(self, game, position):
        self.game = game
        self.starting_coordinate = [position.x, position.y]
        self.grid_coordinate = position
        self.pixel_coordinate = self.get_pixel_coordinate() 
        self.direction = vector(0, 0)
        self.score = 0
        self.lives = 1
        self.speed = 10
        self.target = None

    
#################### Get pixel co-rds ####################


    def get_pixel_coordinate(self):
        return vector((self.grid_coordinate[0] * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.grid_coordinate[1] * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)


#################### UPDATE ####################

    
    def update_pacman(self, direction):
        self.target = direction
        if self.score != 2000:
            if self.is_time_to_move():
                self.move()
            self.pixel_coordinate += self.direction * self.speed

        self.grid_coordinate[0] = (self.pixel_coordinate[0]- INDENT + SQUARE_WIDTH // 2) // SQUARE_WIDTH + 1
        self.grid_coordinate[1] = (self.pixel_coordinate[1] - INDENT + SQUARE_HEIGHT // 2) // SQUARE_HEIGHT + 1
        if self.on_point():
            self.take_point()


#################### Move ####################


    def is_time_to_move(self):
        if int(self.pixel_coordinate.x + HALF_INDENT) % SQUARE_WIDTH == 0:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0) or self.direction == vector(0, 0):
                return True
        if int(self.pixel_coordinate.y + HALF_INDENT) % SQUARE_HEIGHT == 0:
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def move(self):
        self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        x_dir = 0
        y_dir = 0
        if target[0] == 1:
            x_dir = 1
            y_dir = 0
        elif target[1] == 1:
            x_dir = -1
            y_dir = 0
        elif target[2] == 1:
            x_dir = 0
            y_dir = -1
        elif target[3] == 1:
            x_dir = 0
            y_dir = 1

        next_cell = [int(x_dir + self.grid_coordinate[0]), int(y_dir + self.grid_coordinate[1])]

        grid = [[0 for x in range(30)] for x in range(30)]
        for step in self.game.walls:
            if step[0] < 30 and step[1] < 30:
                grid[int(step[1])][int(step[0])] = 1
        if next_cell[0] < 30 and next_cell[1] < 30:
            if grid[next_cell[1]][next_cell[0]] != 1:
                return vector(x_dir, y_dir)
            else:
                return vector(0,0)
        else:
            return vector(0,0)

    def on_point(self): 
        if self.grid_coordinate in self.game.points:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0):
                return True
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def take_point(self):
        self.game.points.remove(self.grid_coordinate)
        self.score += 10
        if len(self.game.points) == 0 or self.score == 1000:
            self.game.is_game_lost = False
    


#################### DISPLAY ####################


    def display_pacman(self):
        self.player_image = pygame.image.load('images/pacman.png')
        if self.direction == vector(0, -1):
            self.player_image = pygame.transform.rotate(self.player_image, 90)
        if self.direction == vector(0, 1):
            self.player_image = pygame.transform.rotate(self.player_image, -90)
        if self.direction == vector(-1, 0):
            self.player_image = pygame.transform.flip(self.player_image, 1, 0)
        self.player_image = pygame.transform.scale(self.player_image, (SQUARE_WIDTH, SQUARE_HEIGHT))
        self.game.screen.blit(self.player_image, (int(self.pixel_coordinate.x - INDENT // 5),int(self.pixel_coordinate.y - INDENT // 5)))

    def display_lives(self):
        for x in range(self.lives):
            self.game.screen.blit(self.player_image, (30 + 20 * x, WINDOW_HEIGHT - 23))