from pygame.math import Vector2 as vector
import pygame, random
from helper import *


class Ghost:
    def __init__(self, game, position, number):
        self.game = game
        self.starting_coordinate = [position.x, position.y]
        self.grid_coordinate = position
        self.direction = vector(0, 0)
        self.target = None
        self.astar = Astar(None, None)
        self.pixel_coordinate = self.get_pixel_coordinate()
        self.number = number
        self.mode = self.ghost_mode()
        self.speed = 4
        

    ##########  Get pixel co-rds  ##########


    def get_pixel_coordinate(self):
        return vector((self.grid_coordinate.x * SQUARE_WIDTH) + HALF_INDENT + SQUARE_WIDTH // 2, (self.grid_coordinate.y * SQUARE_HEIGHT) + HALF_INDENT + SQUARE_HEIGHT // 2)


    ############  Update Ghost  ############


    def update_ghost(self):
        self.target = self.set_target()
        if self.target != self.grid_coordinate:   
            self.pixel_coordinate += self.direction * self.speed
            if self.is_time_to_move():
                self.move()
        self.grid_coords_to_pixel_coords()


    ################  Move  ################


    def set_target(self):
        return self.game.Pacman.grid_coordinate    

    def is_time_to_move(self):
        if int(self.pixel_coordinate.x + INDENT // 2) % SQUARE_WIDTH == 0:
            if self.direction == vector(1, 0) or self.direction == vector(-1, 0) or self.direction == vector(0, 0):
                return True
        if int(self.pixel_coordinate.y + INDENT // 2) % SQUARE_HEIGHT == 0:
            if self.direction == vector(0, 1) or self.direction == vector(0, -1) or self.direction == vector(0, 0):
                return True
        return False

    def move(self):
        
        if self.mode == 'random':
            self.direction = self.ghost_random_move()
        else:
            self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        next_square = self.get_next_square(target)
        x = next_square[1] - self.grid_coordinate[0]
        y = next_square[0] - self.grid_coordinate[1]
        return vector(x, y)

    def get_next_square(self, target):
        map = [[0 for x in range(30)] for x in range(30)]
        for step in self.game.walls:
            if step[0] < 30 and step[1] < 30:
                map[int(step[1])][int(step[0])] = 1
        path = self.astar.run_astar(map, (int(self.grid_coordinate[1]), int(self.grid_coordinate[0])), (int(target[1]), int(target[0])))
        return path[1]

    def grid_coords_to_pixel_coords(self):
        self.grid_coordinate[0] = (self.pixel_coordinate[0] - INDENT + SQUARE_WIDTH // 2) // SQUARE_WIDTH + 1
        self.grid_coordinate[1] = (self.pixel_coordinate[1] - INDENT + SQUARE_HEIGHT // 2) // SQUARE_HEIGHT + 1

    def ghost_random_move(self):
        while True:
            number = random.randint(0, 3)
            if number == 0:
                x_dir, y_dir = 1, 0
            elif number == 1:
                x_dir, y_dir = 0, 1
            elif number == 2:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vector(self.grid_coordinate.x + x_dir, self.grid_coordinate.y + y_dir)
            if next_pos not in self.game.walls:
                break
        return vector(x_dir, y_dir)

    def ghost_mode(self):
        if self.number == 0 or self.number == 1:
            return "random"
        else:
         return "speedy"


    ##############  Display  ###############


    def display_ghost(self):
        self.player_image = pygame.image.load('images/ghost.png')
        self.player_image = pygame.transform.scale(self.player_image, (SQUARE_WIDTH, SQUARE_HEIGHT))
        self.game.screen.blit(self.player_image, (int(self.pixel_coordinate.x - INDENT // 5),int(self.pixel_coordinate.y - INDENT // 5)))


    #################  A*  #################

    def Alg(self, start, target):
            map = [[0 for x in range(ROWS)] for x in range(COLUMNS)]
            for wall in self.game.walls:
                if wall.x < ROWS and wall.y < COLUMNS:
                    map[int(wall.y)][int(wall.x)] = 1
            queue = [start]
            path = []
            visited = []
            while queue:
                current = queue[0]
                queue.remove(queue[0])
                visited.append(current)
                if current == target:
                    break
                else:
                    neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                    for neighbour in neighbours:
                        if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(map[0]):
                            if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(map):
                                next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                                if next_cell not in visited:
                                    if map[next_cell[1]][next_cell[0]] != 1:
                                        queue.append(next_cell)
                                        path.append({"Current": current, "Next": next_cell})
            shortest = [target]
            while target != start:
                for step in path:
                    if step["Next"] == target:
                        target = step["Current"]
                        shortest.insert(0, step["Current"])
            return shortest

class Astar:
    def __init__(self, parent, pos):
        self.parent = parent
        self.pos = pos
        self.f = 0
        self.g = 0
        self.h = 0

    def __eq__(self, other):
        return self.pos == other.pos

    def run_astar(self, field, firstTarget, lastTarget):
        unchecked_coords = []
        checked_coords = []
        step = 0
        neighbours = ((0, -1), (1, 0), (0, 1), (-1, 0))
        step_limit = (len(field) // 2) ** 2
        first_top = Astar(None, firstTarget)
        first_top.f = 0
        first_top.g = 0
        first_top.h = 0
        last_top = Astar(None, lastTarget)
        last_top.f = 0
        last_top.g = 0
        last_top.h = 0
        unchecked_coords.append(first_top)

        while unchecked_coords:
            step += 1 # 
            curr_checked = unchecked_coords[0]
            curr_unchecked = 0

            for i, coord in enumerate(unchecked_coords):
                if coord.f < curr_checked.f:           # сравниваем значение f
                    curr_checked = coord
                    curr_unchecked = i 

            if step > step_limit: # возвращаем путь, который нашли (с конца)
                path = []
                curr_top = curr_checked
                
                while curr_top is not None:
                    path.append(curr_top.pos)
                    curr_top = curr_top.parent
                return path[::-1] 

            unchecked_coords.pop(curr_unchecked)
            checked_coords.append(curr_checked)

            if curr_checked == last_top:
                path = []
                curr_top = curr_checked
                while curr_top is not None:
                    path.append(curr_top.pos)
                    curr_top = curr_top.parent
                return path[::-1]

            childrens = []

            for neighbour in neighbours:
                top = (curr_checked.pos[0] + neighbour[0], curr_checked.pos[1] + neighbour[1])

                isInRange = [
                    top[0] < 0,
                    top[1] < 0,
                    top[0] > (len(field) - 1),
                    top[1] > (len(field[len(field) - 1]) - 1)
                ]

                if any(isInRange): # если в графе
                    continue

                if field[top[0]][top[1]] != 0:
                    continue

                newTop = Astar(curr_checked, top)

                childrens.append(newTop)

            for child in childrens:
                if len([node_child for node_child in checked_coords if node_child == child]) > 0:
                    continue

                child.g = curr_checked.g + 1
                child.h = ((child.pos[0] - last_top.pos[0]) ** 2) + ((child.pos[1] - last_top.pos[1]) ** 2)
                child.f = child.g + child.h

                if len([index_child for index_child in unchecked_coords if child == index_child and child.g > index_child.g]) > 0:
                    continue

                unchecked_coords.append(child)