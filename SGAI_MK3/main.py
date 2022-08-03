import os
import sys
import pygame
from Board import Board
import PygameFunctions as PF
import random as rd
import copy
from ExitPoint import ExitPoint
import DataCollection as DC
import numpy as np
import time

# Constants
OFFSET = 50                    # Number of pixels to offset grid to the top-left side
DAYS_TO_DEATH = 100            # The number of days until there is a 50% chance of death
SHOW_EPSILON_GRAPH = True
AI_TYPE = "DEEP"
ACTION_NUM = 8

# Player controlled variables
# Defaulted to these values
HUMAN_PLAY = True
SHOW_EVERY_FRAME = False       # Will show each action taken by AI if True. Shows only last frame if False.
ROWS = 30
COLUMNS = 30
CELL_DIMENSIONS = 20           # Number of pixels for each cell
BOARD_SIZE = 3
EXIT_POINTS = 4


# Game screen and uncontrolled (not controlled by player) variables
title_screen = True
settings_screen = False
instruction_screen = False
game_active = False
game_over = False
AmountExited = 0
turns_taken = 0

while not game_active:
    # Initializes title screen
    while title_screen:
        PF.main_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Allows player to start game by pressing a key (space)                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    title_screen = False
                    game_active = True
                                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PF.settings_rect.collidepoint(event.pos):
                    settings_screen = True
                    title_screen = False
                if PF.instruction_rect.collidepoint(event.pos):
                    instruction_screen = True
                    title_screen = False

    # Initializes and opens settings screen
    while settings_screen:
        PF.settings_screen(HUMAN_PLAY, BOARD_SIZE, SHOW_EVERY_FRAME)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Player input determines the game's settings    
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Player (human or AI) changes depending on player input
                if PF.AI_box.collidepoint(event.pos):
                    HUMAN_PLAY = False
                if PF.human_box.collidepoint(event.pos):
                    HUMAN_PLAY = True
                if PF.back_rect.collidepoint(event.pos):
                    settings_screen = False
                    title_screen = True
                    
                # Gameboard size changes depending on player input
                if PF.small_box.collidepoint(event.pos): 
                    BOARD_SIZE = 1
                    ROWS, COLUMNS = 10, 10
                    CELL_DIMENSIONS = 60
                    EXIT_POINTS = 1
                if PF.medium_box.collidepoint(event.pos):
                    BOARD_SIZE = 2
                    ROWS, COLUMNS = 20, 20
                    CELL_DIMENSIONS = 30
                    EXIT_POINTS = 2
                if PF.large_box.collidepoint(event.pos):
                    BOARD_SIZE = 3
                    ROWS, COLUMNS = 30, 30
                    CELL_DIMENSIONS = 20
                    EXIT_POINTS = 4
                
                # Actions shown changes depending on player input
                if PF.all_actions_box.collidepoint(event.pos):
                    SHOW_EVERY_FRAME = True
                if PF.last_action_box.collidepoint(event.pos):
                    SHOW_EVERY_FRAME = False
    while instruction_screen:
        PF.instruction_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Returns the user to the title screen if the back button is pressed
                if PF.back_rect.collidepoint(event.pos): 
                    instruction_screen = False
                    title_screen = True


if not HUMAN_PLAY:
    #rd.seed(1)
    if AI_TYPE == "DEEP":
        import stable_baselines3 as sb3 # pip install stable-baselines3[extra]


        print("getting model")
        trained_model = sb3.DQN.load("DQN_agent")


# Player role variables
player_role = "Government"      # Valid options are "Government" and "Zombie"
roleToRoleNum = {"Government": 1, "Zombie": -1}
roleToRoleBoolean = {"Government": False, "Zombie": True}

# Create the game board
GameBoard = Board((ROWS, COLUMNS), OFFSET, CELL_DIMENSIONS, roleToRoleNum[player_role])
GameBoard.populate()

# Self play variables
alpha = 0.2       # learning rate:   the rate that the AI learns
gamma = 0.9       # discount factor: discount for future rewards
epsilon = 0.8     # the percent of time to take the best action (instead of random)
if HUMAN_PLAY:
    episodes = 1
else:
    episodes = 100    # Number of episodes to run reinforcement learning
Original_Board = copy.deepcopy(GameBoard)

epsilon_list = []
survivor_list = []
if SHOW_EPSILON_GRAPH and not HUMAN_PLAY:
    import matplotlib.pyplot as plt     #pip install matplotlib
    fig, ax = plt.subplots()
    ax.set_xlabel("epsilon (random)")
    ax.set_ylabel("mean survival")
    epsilon_range = range(0, 11)
else:
    # this uses the epsilon setting from above
    epsilon_range = range(int(epsilon * 10), int((epsilon * 10) + 1))

# Load images
PF.load_images(GameBoard)

for epsilon_inc in epsilon_range:
    epsilon = float(epsilon_inc) / 10
    if len(epsilon_range) > 1:
        print(f"Trying epsilon of {epsilon}")

    # Reset the Q Table between runs
    if not HUMAN_PLAY:
        if AI_TYPE == "STATE":
            QTable = []  # To be used for reinforcement learning
            for s in range(ROWS * COLUMNS):
                QTable.append([0] * ACTION_NUM)  # (4 x move) + (4 x vaccinate)
        elif AI_TYPE == "SENSE":
            possible_entries = ['V', 'U', 'X', 'I', 'E']
            QTable2 = {}
            for a in possible_entries:  # up
                QTable2[a] = {}
                for b in possible_entries:  # right
                    QTable2[a][b] = {}
                    for c in possible_entries:  # down
                        QTable2[a][b][c] = {}
                        for d in possible_entries:  # left
                            QTable2[a][b][c][d] = [0] * ACTION_NUM
        elif AI_TYPE == "DEEP":
            pass

    
    episodes_ran = 0
    survivors = []
    while episodes > episodes_ran:
        # Increment the episode counter
        episodes_ran += 1
        
        # Create exit points and assign them locations
        ExitPoints = [] #create list of Exit Points
        for i in range(EXIT_POINTS): #create the amount of points specified by the EXIT_POINTS constant
            ExitPoints.append(ExitPoint(rd.randint(0, int(ROWS * COLUMNS) - 1))) #create exit point with random location on the board
        # ExitPoints is now the list with all of the ExitPoint objects
        
        if episodes_ran > 1:
            PF.run(GameBoard, ExitPoints, AmountExited, episodes_ran, rl_episodes = True)
            pygame.display.update()
            print(f"  Episode #{episodes_ran} ended with {alive_count + AmountExited} alive.")
            GameBoard = copy.deepcopy(Original_Board)
        
        AmountExited = 0
        
        # Create list to hold every action per game for data collection
        every_turn = []
    
        running = True
        while running:
            # Allows the pygame window to be moved during execution without freezing
            pygame.event.pump()
            
            # Update the display
            if HUMAN_PLAY or SHOW_EVERY_FRAME:
                if not game_over:
                    if not HUMAN_PLAY:
                        PF.run(GameBoard, ExitPoints, AmountExited, episodes_ran, rl_episodes = True)
                    else:
                        PF.run(GameBoard, ExitPoints, AmountExited, episodes_ran, rl_episodes = False)
                    pygame.display.update()
            
            # Get the (human or AI) player's intention for their turn
            player_moved = False
            if HUMAN_PLAY:
                player_action = []
                for event in pygame.event.get():    # Event Handling
                    if event.type == pygame.MOUSEBUTTONUP:
                        x, y = event.pos[0], event.pos[1]
                        button_pressed = event.button
                        player_loc = GameBoard.toCoord(GameBoard.state[GameBoard.govt_index].location)
                        grid_location_clicked = PF.get_grid_clicked(GameBoard, x, y)
                        
                        if grid_location_clicked:   # Only proceed if a valid grid cell was clicked
                            # Determine the type of activity the user intends
                            if button_pressed == 1:     # Left mouse button
                                player_action = ["move"]
                            elif button_pressed == 3:   # Right mouse button
                                player_action = ["vaccinate"]
                            
                            # Figure out which way the user clicked relative to the government player
                            if player_loc[0] == grid_location_clicked[0]:
                                if player_loc[1] == (grid_location_clicked[1] - 1):
                                    player_action.append("down")
                                elif player_loc[1] == (grid_location_clicked[1] + 1):
                                    player_action.append("up")
                                elif player_loc[1] == grid_location_clicked[1]:
                                    player_action = ["pass"]    # Overwrites the ["move"] currently in player_action
                            elif player_loc[1] == grid_location_clicked[1]:
                                if player_loc[0] == (grid_location_clicked[0] - 1):
                                    player_action.append("right")
                                elif player_loc[0] == (grid_location_clicked[0] + 1):
                                    player_action.append("left")
                            
                            # Determine set of possible moves given current state
                            possible_moves = PF.get_possible_moves(GameBoard, player_loc, True)
                            
                            # Check if the move is valid
                            if player_action in possible_moves:
                                player_moved = True
                    
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            player_action = ["move", "up"]
                        elif event.key == pygame.K_DOWN:
                            player_action = ["move", "down"]
                        elif event.key == pygame.K_LEFT:
                            player_action = ["move", "left"]
                        elif event.key == pygame.K_RIGHT:
                            player_action = ["move", "right"]
                        elif event.key == pygame.K_SPACE:
                            player_action = ["pass"]
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                        
                        # Determine set of possible moves given current state
                        player_loc = GameBoard.toCoord(GameBoard.state[GameBoard.govt_index].location)
                        possible_moves = PF.get_possible_moves(GameBoard, player_loc, True)
                        
                        # Check if the move is valid
                        if player_action in possible_moves:
                            player_moved = True
                    elif event.type == pygame.QUIT:
                        running = False
                        exit()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                
                # Get the current player location and determine a list of all possible moves
                player_loc = GameBoard.toCoord(GameBoard.state[GameBoard.govt_index].location)
                player_ind = GameBoard.toIndex(player_loc)
                possible_moves = PF.get_possible_moves(GameBoard, player_loc, True)
                
                # If there are no possible actions other than passing, then pass
                # Otherwise, use reinforcement learning to select an action
                if len(possible_moves) == 1:
                    player_action = ["pass"]
                elif AI_TYPE == "STATE":    # Using QLearning with state
                    # Select one of the possible moves using the greedy epsilon method and set it in player_action
                    player_action, choice = PF.greedy_epsilon(epsilon, QTable[player_ind])
                    while player_action not in possible_moves:
                        reward = -1000
                        QTable[GameBoard.govt_index][choice] = PF.update_Q_value(
                            QTable[player_ind][choice],
                            alpha,
                            reward,
                            gamma,
                            QTable[player_ind][choice]
                        )
                        player_action, choice = PF.greedy_epsilon(epsilon, QTable[player_ind])
                elif AI_TYPE == "SENSE":   # Using QLearning with a sensory state
                    l = GameBoard.sense_nearby()
                    player_action, choice = PF.greedy_epsilon(epsilon, QTable2[l[0]][l[1]][l[2]][l[3]])
                    while player_action not in possible_moves:
                        reward = -1000
                        QTable2[l[0]][l[1]][l[2]][l[3]][choice] = PF.update_Q_value(
                            QTable2[l[0]][l[1]][l[2]][l[3]][choice],
                            alpha,
                            reward,
                            gamma,
                            max(QTable2[l[0]][l[1]][l[2]][l[3]])
                        )
                        player_action, choice = PF.greedy_epsilon(epsilon, QTable2[l[0]][l[1]][l[2]][l[3]])
                elif AI_TYPE == "DEEP": # Using Deep QLearning
                    # Have AI select a action.
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
                    MAX_NUM_INDEX = 5
                    time.sleep(1)
                    # Get the current map in 1D
                    num_dict = {'V': 0, 'U': 1, 'X': 2, 'I': 3, 'E': 4}
                    ret = []
                    for i in GameBoard.state:
                        ret.append(num_dict[GameBoard.state_contents_to_char(i)])

                    # Put the agent position on the map
                    ret[GameBoard.govt_index] = 5

                    # Normalize
                    ret = np.array(ret, dtype=np.float32)
                    ret /= np.float32(MAX_NUM_INDEX)
                    ret -= np.float32(0.5)
                    print(ret)
                    chosen_action = trained_model.predict(ret, deterministic=True)
                    print(f"chosen_action:{chosen_action}")
                    player_action = ACTION_MAPPINGS[chosen_action[0]]
                    print(f"player_action:{player_action}")
                    if player_action not in possible_moves:
                        print("not valid")
                        player_action = ["pass"]
                    
                player_moved = True
            
            # If the player or AI has selected an action, then the simulation can advance one step
            if player_moved:   
                turns_taken += 1
                DC.steps_taken(player_action, every_turn)
                
                # Implement the player's action
                # Doesn't check for "pass" since nothing needs to change
                if player_action[0] == "move":
                    GameBoard.move(player_action[1], player_loc, True)
                elif player_action[0] == "vaccinate":
                    GameBoard.vaccinate(player_action[1], player_loc)

                # Allow all the people in the simulation to have a turn now
                PF.simulate(GameBoard, ExitPoints)

                # People die!
                PF.progress_infection(GameBoard, DAYS_TO_DEATH)
                
                # Determine all of the living people on the board after each move
                alive_count = GameBoard.num_alive()

                # If the AI is playing, then implement reinforcement learning
                if not HUMAN_PLAY:
                    if AI_TYPE == "STATE":
                        # Figure out the reward for the action selected
                        #reward = PF.reward(oldGameboard, GameBoard, player_action)
                        reward = PF.reward(GameBoard, GameBoard, player_action)
                        # Update the Q-Table
                        # player_ind is the location of the player at the old location
                        QTable[player_ind][choice] = PF.update_Q_value(
                            QTable[player_ind][choice],
                            alpha,
                            reward,
                            gamma,
                            max(QTable[GameBoard.state[GameBoard.govt_index].location])
                        )
                    elif AI_TYPE == "SENSE":
                        reward = PF.reward2(player_action, GameBoard)
                        new = GameBoard.sense_nearby()
                        QTable2[l[0]][l[1]][l[2]][l[3]][choice] = PF.update_Q_value(
                            QTable2[l[0]][l[1]][l[2]][l[3]][choice],
                            alpha,
                            reward,
                            gamma,
                            max(QTable2[new[0]][new[1]][new[2]][new[3]]))
                        
                #iterate through each exitpoint to check if a person is inside of them
                #create an empty "amount" variable to store the amount of people who exited this round
                for Exit in ExitPoints:
                    AmountExited += Exit.CheckPeopleExited(GameBoard.people, GameBoard) #returns a "1" if someone exited, returns a 0 if no one was in exit

                # Ends the game when there are no more infected alive
                # Can also end the game if no humans are left on the board
                if GameBoard.num_infected() == 0 or alive_count == 1:
                    survivors.append(GameBoard.population + AmountExited)
                    DC.data_collection(HUMAN_PLAY, every_turn, GameBoard, turns_taken, AmountExited, BOARD_SIZE)
                    # Game over screen is only active during human play
                    if HUMAN_PLAY:  #or episodes_ran % 100 == 0 or episodes_ran == episodes
                        PF.display_finish_screen(GameBoard, AmountExited)
                        game_over = True
                        while HUMAN_PLAY:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()

                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_SPACE:
                                        os.execl(sys.executable, sys.executable, *sys.argv)

                    PF.run(GameBoard, ExitPoints, AmountExited, episodes_ran, rl_episodes = True)
                    turns_taken = 0
                    running = False

    # Store the current conditions
    epsilon_list.append(epsilon)
    survivor_list.append(sum(survivors) / len(survivors))

print(f"Mean # of surviving people was {sum(survivors) / len(survivors)}.")

if SHOW_EPSILON_GRAPH and not HUMAN_PLAY:
    ax.plot(epsilon_list, survivor_list)
    plt.show()