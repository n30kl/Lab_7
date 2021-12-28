import numpy as np
import torch, random
from collections import deque
from model import Linear_QNet, QTrainer


class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.batch_size = 1000
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen = 100_000)
        self.model = Linear_QNet(900, 300, 4)
        self.trainer = QTrainer(self.model, 0.001, gamma = self.gamma)


    def remember(self, state, direction, reward, next_state, done):
        self.memory.append((state, direction, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory(self):
        if len(self.memory) > self.batch_size:
            mini_sample = random.sample(self.memory, self.batch_size)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    
    def get_direction(self, state):
        direction = [0, 0, 0, 0]
        self.epsilon = 1000 - self.number_of_games
        if random.randint(0, 400) < self.epsilon:
            move = random.randint(0, 3)
            direction[move] = 1
        else:
            state = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state)
            move = torch.argmax(prediction).item()
            direction[move] = 1

        return direction