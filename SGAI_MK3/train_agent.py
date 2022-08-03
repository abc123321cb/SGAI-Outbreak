import gym
import stable_baselines3 as sb3 # pip install stable-baselines3[extra]
import sys
import numpy as np
import random as rd
import pygame
sys.path.append("./")

from Board import Board
from ExitPoint import ExitPoint
import PygameFunctions as PF

import matplotlib.pyplot as plt     #pip install matplotlib
fig, ax = plt.subplots()
ax.set_xlabel("# of steps")
ax.set_ylabel("# of invalid moves")
num_of_moves = []
num_of_invalid_moves = []

TIMESTEPS_TRAINING = 50000000
PERCENT_TO_SHOW = 1
SHOW_DEBUG = False

class ZombieEnvironment(gym.Env):
    ACTION_SPACE = tuple(range(8))
    ACTION_MAPPINGS = {
        0: ["vaccinate", "left"],
        1: ["vaccinate", "right"],
        2: ["vaccinate", "up"],
        3: ["vaccinate", "down"],
        4: ["move", "left"],
        5: ["move", "right"],
        6: ["move", "up"],
        7: ["move", "down"]
    }
    EXIT_POINTS = 0
    ROWS = 10
    COLUMNS = 10
    SIZE = (COLUMNS, ROWS)
    DAYS_TO_DEATH = 100            # The number of days until there is a 50% chance of death

    def __init__(self, max_timesteps: int = 300, have_enemy_player: bool = True):
        self.max_timesteps = max_timesteps
        self.reset()
        self.total_timesteps = 0
        self.total_invalid_moves = 0
        self.have_enemy_player = have_enemy_player
        self.ExitPoints = [] #create list of Exit Points
        self.AmountExited = 0
        self.action_space = gym.spaces.Discrete(len(ZombieEnvironment.ACTION_MAPPINGS))
        self.observation_space = gym.spaces.Box(-0.5, 0.5, (ZombieEnvironment.ROWS * ZombieEnvironment.COLUMNS,))

    def reset(self):
        self.board = None
        self.board = Board(ZombieEnvironment.SIZE, 50, 20, 1)
        self.board.populate()

        if SHOW_DEBUG:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        self.ExitPoints = [] #create list of Exit Points
        for i in range(ZombieEnvironment.EXIT_POINTS): #create the amount of points specified by the EXIT_POINTS constant
            self.ExitPoints.append(ExitPoint(rd.randint(0, int(ZombieEnvironment.ROWS * ZombieEnvironment.COLUMNS) - 1))) #create exit point with random location on the board
        self.done = False

        # coordinates of the agent (1D)
        self.agentPosition = self.board.govt_index

        # useful for metrics
        self.episode_invalid_actions = 0
        self.episode_reward = 0
        self.episode_timesteps = 0
        
        self.AmountExited = 0

        return self._get_obs()

    def state_to_str(self):
        num = -1
        index = -1
        this_str = ""
        for i in self.board.state:
            num += 1
            index += 1
            if num > (ZombieEnvironment.COLUMNS - 1):
                num = 0
                print(this_str)
                this_str = ""

            if index == self.board.govt_index:
                this_str += "*"
            else:
                this_str += self.board.state_contents_to_char(i)
        print(this_str)

    def step(self, action: int):
        action_name = ZombieEnvironment.ACTION_MAPPINGS[action]
        
        # get the current player's location
        player_loc = self.board.toCoord(self.board.govt_index)
        # check if move is valid
        valid = False
        possible_moves = PF.get_possible_moves(self.board, player_loc, True)
        for elem in possible_moves:
            if action_name == elem:
                valid = True

        if SHOW_DEBUG:
            self.state_to_str()
            print(f"Player located at {player_loc}")
            print(f"Agent decides to move {action_name}")
            print(f"Possible moves include {possible_moves}")
            print(f"So this move is {'valid' if valid else 'not valid'}")

        # if the action is valid, then move the agent and get the new position
        if valid:
            if action_name[0] == "move":
                self.board.move(action_name[1], player_loc, True)
            elif action_name[0] == "vaccinate":
                self.board.vaccinate(action_name[1], player_loc)
            new_pos = self.board.toCoord(self.board.govt_index)
            
            # Update the agent position
            self.agentPosition = self.board.govt_index
        
        won = None

        # Allow all the people in the simulation to have a turn now
        PF.simulate(self.board, self.ExitPoints)

        # People die!
        PF.progress_infection(self.board, ZombieEnvironment.DAYS_TO_DEATH)

        # Determine all of the living people on the board after each move
        alive_count = self.board.num_alive()

        for Exit in self.ExitPoints:
            self.AmountExited += Exit.CheckPeopleExited(self.board.people, self.board) #returns a "1" if someone exited, returns a 0 if no one was in exit

        # if nobody is alive except you, then you lose
        if alive_count == 1:
            self.done = True
            won = False

        # the game is over if nobody left is infected
        if self.board.num_infected() == 0:
            self.done = True
            won = True

        # Allow episode to end after a max number of turns
        if self.episode_timesteps > self.max_timesteps:
            self.done = True

        # Episode ends for invalid move
        if not valid:
            self.done = True

        # get obs, reward, done, info
        obs = self._get_obs()
        reward = self._get_reward(action_name, valid, won)
        done = self._get_done()
        info = self._get_info()

        if SHOW_DEBUG:
            print(f"The reward for this move is {reward}")
            print()

        # update the metrics
        self.episode_reward += reward
        if not valid:
            self.episode_invalid_actions += 1
            self.total_invalid_moves += 1
        self.episode_timesteps += 1
        self.total_timesteps += 1

        if (self.total_timesteps * (100 / PERCENT_TO_SHOW)) % TIMESTEPS_TRAINING == 0:
            print(f"{(self.total_timesteps * 100.0) / TIMESTEPS_TRAINING}% - {self.total_invalid_moves}")
            num_of_moves.append( (self.total_timesteps * 100.0) / TIMESTEPS_TRAINING )
            num_of_invalid_moves.append( self.total_invalid_moves )
            self.total_invalid_moves = 0

        # return the obs, reward, done, info
        return obs, reward, done, info

    def _get_info(self):
        return {}

    def _get_done(self):
        return self.done

    def _get_reward(self, action_name, was_valid: bool, won: bool):
        """
        Return reward between [-1, 1]
        """
        # Punish for not valid move
        if not was_valid:
            return -100
        
        # Punish for saving nobody
        if won is False:
            return -1

        # Reward for vaccinating
        if action_name[0] == "vaccinate":
            return 10

        # Base reward for any other move
        return 0
        return -0.1

    def _get_obs(self):
        """
        Return a 1D list of the state map
        Normalized from -0.5 to 0.5
        """
        MAX_NUM_INDEX = 5
        
        # Get the current map in 1D
        num_dict = {'V':0, 'U':1, 'X':2, 'I':3, 'E':4}
        ret = []
        for i in self.board.state:
            ret.append( num_dict[self.board.state_contents_to_char(i)] )
        
        # Put the agent position on the map
        ret[self.board.govt_index] = 5

        # Normalize
        ret = np.array(ret, dtype=np.float32)
        ret /= np.float32(MAX_NUM_INDEX)
        ret -= np.float32(0.5)
        return ret  # 1D list

    def render(self):
        pass
        PF.run(self.board)
        pygame.display.update()

    def init_render(self):
        pass
        PF.initScreen(self.board)
        pygame.display.update()

    def close(self):
        pygame.quit()

pygame.quit()
env = ZombieEnvironment(50)

model = sb3.DQN("MlpPolicy", env, learning_rate=0.001, learning_starts=5000)
model.learn(TIMESTEPS_TRAINING)
model.save("DQN_agent")

ax.plot(num_of_moves, num_of_invalid_moves)
plt.show()