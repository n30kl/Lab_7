from pygame.math import Vector2 as vector
import sys, pygame, skimage
from diagram import plot
from helper import *
from pacman import *
from ghost import *
from agent import *


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_game_launched = True
        self.is_game_lost = True
        self.agent = Agent()
        self.walls, self.points, self.ghosts = [], [], []
        self.ghost_cords = []
        self.pacman_cord = None
        self.generate_level()
        self.create_ghosts()
        self.Pacman = Pacman(self, vector(self.pacman_cord))
        self.diagram_score = []
        self.diagram_average_score = []
        self.sum_score = 0
        self.best_score = 0

    
    def get_state(self):
        image = skimage.color.rgb2gray(pygame.surfarray.array3d(pygame.display.get_surface()))
        image = skimage.transform.resize(image, (30, 30))
        return np.array(image).flatten()
        

    ##############  Run Game  ##############


    def run_game(self):
        
        while self.is_game_launched:
            self.clock.tick(FPS)
            self.exit_by_esc()
            self.game_display()

            state = self.get_state()
            direction = self.agent.get_direction(state)
            reward, is_game_running, score = self.game_update(direction)
            new_state = self.get_state()
            self.agent.train_short_memory(state, direction, reward, new_state, is_game_running)
            self.agent.remember(state, direction, reward, new_state, is_game_running)

            if is_game_running == False:
                self.agent.number_of_games += 1
                self.agent.train_long_memory()
    
                if score > self.best_score:
                    self.best_score = score
                    self.agent.model.save()
                    
                print("Game", self.agent.number_of_games, 'Score', score, 'Best Score', self.best_score)    
                self.diagram_score.append(score)
                self.sum_score += score
                mean_score = self.sum_score / self.agent.number_of_games
                self.diagram_average_score.append(mean_score)
                plot(self.diagram_score, self.diagram_average_score)

                self.reset_game()
                

        pygame.quit()
        sys.exit() 


    ###########  Generate Level  ###########


    def generate_level(self):
        self.background = pygame.image.load('images/background.jpg')
        self.background = pygame.transform.scale(self.background, (MAP_WIDTH, MAP_HEIGHT))
        with open("maze.txt", 'r') as file:
            for y, line in enumerate(file):
                for x, sign in enumerate(line):
                    if sign == "w":
                        self.walls.append(vector(x, y))
                    elif sign == "p":
                        self.points.append(vector(x, y))
                    elif sign == "U":
                        self.pacman_cord = [x, y]
                    elif sign in ["1", "2", "3", "4"]:
                        self.ghost_cords.append([x, y])


    ###########  Create Ghosts  ############


    def create_ghosts(self):
        for ghost, position in enumerate(self.ghost_cords):
            self.ghosts.append(Ghost(self, vector(position), ghost))


    #############  Reset Game  #############
    

    def reset_game(self):
        self.is_game_lost = True
        self.walls = []
        self.points = []    
        self.Pacman.score = 0    
        self.reset_pacman()
        self.reset_ghosts()
        self.generate_level() 

    def reset_pacman(self, isReset = True):
        if isReset:
            self.Pacman.lives = 1
        self.Pacman.grid_coordinate = vector(self.Pacman.starting_coordinate)
        self.Pacman.pixel_coordinate = self.Pacman.get_pixel_coordinate()
        self.Pacman.direction *= 0
        self.pacman_cord = None

    def reset_ghosts(self):
        self.ghost_cords = []
        for ghost in self.ghosts:
            ghost.grid_coordinate = vector(ghost.starting_coordinate)
            ghost.pixel_coordinate = ghost.get_pixel_coordinate()
            ghost.direction *= 0


    ############  Game Update  ############


    def game_update(self, direction):
        cur_score = self.Pacman.score
        cur_lives = self.Pacman.lives

        self.Pacman.update_pacman(direction)
        for ghost in self.ghosts:
            ghost.update_ghost()
            if ghost.grid_coordinate == self.Pacman.grid_coordinate:
                self.delete_life()

        reward = 0
        if cur_score < self.Pacman.score:
            reward = 1
        if cur_lives > self.Pacman.lives:
            reward = -1

        return reward, self.is_game_lost, self.Pacman.score

        
    ############  Delete Life  ############


    def delete_life(self):
        self.Pacman.lives -= 1
        if self.Pacman.lives == 0:
            self.is_game_lost = False
        else:
            self.reset_pacman(False)
            self.reset_ghosts()


    ##############  Display  ##############


    def game_display(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.background, (HALF_INDENT, HALF_INDENT))
        self.display_text(f'SCORE: {self.Pacman.score}', self.screen, [280, 0], 18, TEXT_COLOR, FONT)
        self.display_lines()
        self.display_walls()
        self.display_points()
        self.Pacman.display_pacman()
        self.Pacman.display_lives()
        for ghost in self.ghosts:
            ghost.display_ghost()
        pygame.display.update()
        
    def display_lines(self):
        for x in range(X_LINE):
            pygame.draw.line(self.background, LINES_COLOR, (x * SQUARE_WIDTH, 0), (x * SQUARE_WIDTH, WINDOW_HEIGHT))
        for y in range(Y_LINE):
            pygame.draw.line(self.background, LINES_COLOR, (0, y * SQUARE_HEIGHT), (WINDOW_WIDTH, y * SQUARE_HEIGHT))

    def display_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.background, WALL_COLOR, (wall.x * SQUARE_WIDTH, wall.y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))

    def display_points(self):
        for point in self.points:
            pygame.draw.circle(self.screen, POINT_COLOR, (int(point.x * SQUARE_WIDTH) + SQUARE_WIDTH // 2 + HALF_INDENT, int(point.y * SQUARE_HEIGHT) + SQUARE_HEIGHT // 2 + HALF_INDENT), 5)

    def display_text(self, words, screen, position, size, colour, fontName, centered = False):
        font = pygame.font.SysFont(fontName, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            position[0] = position[0] - text_size[0] // 2
            position[1] = position[1] - text_size[1] // 2
        screen.blit(text, position)


    #############  Close Game  #############


    def exit_by_esc(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_game_launched = False


pygame.init()
game = Game().run_game()