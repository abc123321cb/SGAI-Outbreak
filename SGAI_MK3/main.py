import random
import sys

import pygame
from Board import Board
import PygameFunctions as PF
import random as rd
import time
import copy

# Constants
HUMAN_PLAY = False
ROWS = 30
COLUMNS = 30
OFFSET = 50                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = 20           # Number of pixels for each cell
DAYS_TO_DEATH = 100            # The number of days until there is a 50% chance of death

if not HUMAN_PLAY:
    rd.seed(1)

# Player role variables
player_role = "Government"      # Valid options are "Government" and "Zombie"
roleToRoleNum = {"Government": 1, "Zombie": -1}
roleToRoleBoolean = {"Government": False, "Zombie": True}

# Create the game board
GameBoard = Board((ROWS, COLUMNS), OFFSET, CELL_DIMENSIONS, roleToRoleNum[player_role])
GameBoard.populate()

# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 100
epochs_ran = 0
Original_Board = copy.deepcopy(GameBoard)
QTable = []  # To be used for reinforcement learning
for s in range(ROWS * COLUMNS):
    QTable.append([0] * 8)

# Load images
PF.load_images(GameBoard)


while epochs > epochs_ran:
    epochs_ran += 1
    GameBoard = copy.deepcopy(Original_Board)
    print(epochs_ran)
    running = True
    while running:
        if HUMAN_PLAY or epochs == epochs_ran:
            # update the display
            PF.run(GameBoard)
            pygame.display.update()

        # Get the (human or AI) player's intention for their turn
        player_moved = False
        if HUMAN_PLAY:
            for event in pygame.event.get():    # Event Handling
                if event.type == pygame.MOUSEBUTTONUP:
                    player_action = []
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
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                    player_loc = GameBoard.toCoord(GameBoard.state[GameBoard.govt_index].location)

                    # Determine set of possible moves given current state
                    possible_moves = PF.get_possible_moves(GameBoard, player_loc, True)

                    # Check if the move is valid
                    if player_action in possible_moves:
                        player_moved = True
                elif event.type == pygame.QUIT:
                    running = False
                    sys.exit()
        else:
            # Add code to allow an AI to select an action given the current state
            # The action should be a two-dimensional list [intention, direction]

            # Determine a list of all possible moves
            player_loc = GameBoard.toCoord(GameBoard.state[GameBoard.govt_index].location)
            player_ind = GameBoard.toIndex(player_loc)
            possible_moves = PF.get_possible_moves(GameBoard, player_loc, True)

            # Need a method to select one of the possible moves and set it in player_action
            player_action, choice = PF.greedy_epsilon(epsilon, QTable[player_ind])

            while player_action not in possible_moves:
                reward = -1000
                QTable[GameBoard.govt_index][choice] = PF.update_Q_value(
                    (QTable[player_ind])[choice], alpha, reward, gamma,
                    (QTable[player_ind])[choice])
                player_action, choice = PF.greedy_epsilon(epsilon, QTable[player_ind])



            player_moved = True

        if player_moved:   # The player has selected an action
            oldGameboard = copy.deepcopy(GameBoard)
            # Implement the player's action
            Past_location = GameBoard.govt_index
            if player_action[0] == "move":
                GameBoard.move(player_action[1], player_loc, True)
            elif player_action[0] == "vaccinate":
                GameBoard.vaccinate(player_action[1], player_loc)


            # Allow all the people in the simulation to have a turn now
            PF.simulate(GameBoard)

            # People die!
            PF.progress_infection(GameBoard, DAYS_TO_DEATH)

            if not HUMAN_PLAY:
                reward = PF.reward(oldGameboard, GameBoard, player_action)
                QTable[player_ind][choice] = PF.update_Q_value(
                    QTable[player_ind][choice], alpha, reward, gamma, max(GameBoard.QTable[GameBoard.state[GameBoard.govt_index].location]))

            # Check for end conditions
            if GameBoard.num_infected() == 0:   # There are no infected people left
                if HUMAN_PLAY or epochs_ran % 100 == 0:
                    PF.run(GameBoard)
                    PF.display_finish_screen()
                running = False

print(QTable)
input("enter anything to continue.")