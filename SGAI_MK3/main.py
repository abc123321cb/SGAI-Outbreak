<<<<<<< Updated upstream
=======
from ast import If
import sys
>>>>>>> Stashed changes
import pygame
from Board import Board
import PygameFunctions as PF
import random as rd
<<<<<<< Updated upstream

# Constants
ROWS = 6
COLUMNS = 6
BORDER = 150                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100,100)     # Number of pixels (x,y) for each cell
ACTION_SPACE = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite"]
SELF_PLAY = False
=======
import copy
from ExitPoint import ExitPoint

# Constants
HUMAN_PLAY = True
SHOW_EVERY_FRAME = False       # Will show each action taken by AI if True. Shows only last frame if False.
ROWS = 30
COLUMNS = 30
OFFSET = 50                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = 20           # Number of pixels for each cell
DAYS_TO_DEATH = 100            # The number of days until there is a 50% chance of death
SHOW_EPSILON_GRAPH = False
USE_STATE_QTABLE = False
EXIT_POINTS = 3 #Number of exit points

if not HUMAN_PLAY:
    rd.seed(1)
>>>>>>> Stashed changes

# Player role variables
player_role = "Government"      # Valid options are "Government" and "Zombie"
roleToRoleNum = {"Government": 1, "Zombie": -1}
roleToRoleBoolean = {"Government": False, "Zombie": True}

#Create the game board
GameBoard = Board((ROWS,COLUMNS), BORDER, CELL_DIMENSIONS, roleToRoleNum[player_role])
GameBoard.populate()

#create exit points
ExitPoints = [] #create empty list to store exitpoints in 
for i in range(EXIT_POINTS): #create the amountspecified
    NewExit = ExitPoint((rd.randint(0, int(ROWS * COLUMNS) - 1))) #create the exit point to be added, give a random location
    ExitPoints.append(NewExit) #add to the list

#"ExitPoints" will be the list that is iterated through at the end of each round to check if anything is in exit

# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 1000
epochs_ran = 0
Original_Board = GameBoard.clone(GameBoard.States)


# Initialize variables
running = True
take_action = []
playerMoved = False
font = pygame.font.SysFont("Comic Sans", 20)



while running:
    P = PF.run(GameBoard)

    if SELF_PLAY:
        
        # Event Handling
        for event in P:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = PF.get_action(GameBoard, x, y)
                if action == "heal":                                        # Process a "heal" intention if take_action is currently empty
                    if take_action == []:
                        take_action.append("heal")
                elif action != None:                                        # Otherwise, get the coordinate of a valid grid cell that was clicked
                    idx = GameBoard.toIndex(action)                         # Get the corresponding 1D index from the 2D grid location that was clicked
                    if "move" not in take_action and take_action == []:     # Check that the click corresponds to an intention to move a player
                        # Make sure that the space is not an empty space or a space of the opposite team
                        if ( (GameBoard.States[idx].person is not None) and (GameBoard.States[idx].person.isZombie == roleToRoleBoolean[player_role]) ):
                            take_action.append("move")
                    if take_action != []:                                   # Only append a coordinate if there is a pending "heal" or "move" intention
                        take_action.append(action)
            if event.type == pygame.QUIT:
                running = False
        
        # Display the current action
        PF.screen.blit(
            font.render("Your move is currently:", True, PF.WHITE),
            (800, 400),
        )
        PF.screen.blit(font.render(f"{take_action}", True, PF.WHITE), (800, 450))

        # Action handling
        if len(take_action) > 1:
            if take_action[0] == "move":
                if len(take_action) > 2:
                    directionToMove = PF.direction(take_action[1], take_action[2])
                    result = [False, None]
                    if directionToMove == "moveUp":
                        result = GameBoard.moveUp(take_action[1])
                    elif directionToMove == "moveDown":
                        result = GameBoard.moveDown(take_action[1])
                    elif directionToMove == "moveLeft":
                        result = GameBoard.moveLeft(take_action[1])
                    elif directionToMove == "moveRight":
                        result = GameBoard.moveRight(take_action[1])
                    if result[0] != False:
                        playerMoved = True
                    take_action = []
            elif take_action[0] == "heal":
                result = GameBoard.heal(take_action[1])
                if result[0] != False:
                    playerMoved = True
                take_action = []

        # Computer turn
        if playerMoved:
            pygame.display.update()
            playerMoved = False
            take_action = []
            
            # Make a list of all possible actions that the computer can take
            possible_actions = [
                ACTION_SPACE[i]
                for i in range(6)
                if (i != 4 and player_role == "Government") or (i != 5 and player_role == "Zombie")
            ]
            
            # Figure out all possible moves and select an action
            possible_move_coords = []
            while len(possible_move_coords) == 0 and len(possible_actions) != 0:
                action = rd.choice(possible_actions)
                possible_move_coords = GameBoard.get_possible_moves(action, "Government" if player_role == "Zombie" else "Zombie")
                possible_actions.remove(action)
            
            # No valid moves, player wins
            if len(possible_actions) == 0 and len(possible_move_coords) == 0:
                PF.display_win_screen()
                running = False
                continue
            
            # Select the destination coordinates
            move_coord = rd.choice(possible_move_coords)
            
            # Implement the selected action
            if action == "moveUp":
                GameBoard.moveUp(move_coord)
            elif action == "moveDown":
                GameBoard.moveDown(move_coord)
            elif action == "moveLeft":
                GameBoard.moveLeft(move_coord)
            elif action == "moveRight":
                GameBoard.moveRight(move_coord)
            elif action == "bite":
                GameBoard.bite(move_coord)
            elif action == "heal":
                GameBoard.heal(move_coord)

        # Update the display
        pygame.display.update()

    else:
        if epochs_ran % 100 == 0:
            print("Board Reset!")
            GameBoard = Original_Board  # reset environment
        for event in P:
            i = 0
            r = rd.uniform(0.0, 1.0)
            st = rd.randint(0, len(GameBoard.States) - 1)
            state = GameBoard.QTable[st]

            if r < gamma:
                while GameBoard.States[st].person is None:
                    st = rd.randint(0, len(GameBoard.States) - 1)
            else:
                biggest = None
                for x in range(len(GameBoard.States)):
                    arr = GameBoard.QTable[x]
                    exp = sum(arr) / len(arr)
                    if biggest is None:
                        biggest = exp
                        i = x
                    elif biggest < exp and player_role == "Government":
                        biggest = exp
                        i = x
                    elif biggest > exp and player_role != "Government":
                        biggest = exp
                        i = x
                state = GameBoard.QTable[i]
            b = 0
            j = 0
            ind = 0
            for v in state:
                if v > b and player_role == "Government":
                    b = v
                    ind = j
                elif v < b and player_role != "Government":
                    b = v
                    ind = j
                j += 1
            action_to_take = ACTION_SPACE[ind]
            old_qval = b
            old_state = i
            
<<<<<<< Updated upstream
            # Update
            # Q(S, A) = Q(S, A) + alpha[R + gamma * max_a Q(S', A) - Q(S, A)]
            reward = GameBoard.act(old_state, action_to_take)
            ns = reward[1]
            NewStateAct = GameBoard.QGreedyat(ns)
            NS = GameBoard.QTable[ns][NewStateAct[0]]
            #GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[i]
            if GameBoard.num_zombies() == 0:
                print("winCase")

            take_action = []
            print("Enemy turn")
            ta = ""
            if player_role == "Government":
                r = rd.randint(0, 5)
                while r == 4:
                    r = rd.randint(0, 5)
                ta = ACTION_SPACE[r]
            else:
                r = rd.randint(0, 4)
                ta = ACTION_SPACE[r]
            poss = GameBoard.get_possible_moves(ta, "Zombie")
            
            if len(poss) > 0:
                r = rd.randint(0, len(poss) - 1)
                a = poss[r]
                if ta == "moveUp":
                    GameBoard.moveUp(a)
                elif ta == "moveDown":
                    GameBoard.moveDown(a)
                elif ta == "moveLeft":
                    GameBoard.moveLeft(a)
                elif ta == "moveRight":
                    GameBoard.moveRight(a)
                elif ta == "bite":
                    GameBoard.bite(a)
                elif ta == "heal":
                    GameBoard.heal(a)
            if GameBoard.num_zombies() == GameBoard.population:
                print("loseCase")
            if event.type == pygame.QUIT:
                running = False
=======
            # If the player or AI has selected an action, then the simulation can advance one step
            if player_moved:   
                #oldGameboard = copy.deepcopy(GameBoard)
                
                # Implement the player's action
                # Doesn't check for "pass" since nothing needs to change
                if player_action[0] == "move":
                    GameBoard.move(player_action[1], player_loc, True)
                elif player_action[0] == "vaccinate":
                    GameBoard.vaccinate(player_action[1], player_loc)

                # Allow all the people in the simulation to have a turn now
                PF.simulate(GameBoard)

                # People die!
                PF.progress_infection(GameBoard, DAYS_TO_DEATH)

                # If the AI is playing, then implement reinforcement learning
                if not HUMAN_PLAY:
                    if USE_STATE_QTABLE:
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
                    else:
                        reward = PF.reward2(player_action, GameBoard)
                        new = GameBoard.sense_nearby()
                        QTable2[l[0]][l[1]][l[2]][l[3]][choice] = PF.update_Q_value(
                            QTable2[l[0]][l[1]][l[2]][l[3]][choice],
                            alpha,
                            reward,
                            gamma,
                            max(QTable2[new[0]][new[1]][new[2]][new[3]]))
                
                #Check if any people are in the exitpoint
                AmountExited = 0 #create a Variable to store how many people exited this round
                for Exit in ExitPoints: #iterate thtough all exit points
                    AmountExited += Exit.CheckPeopleExited(GameBoard.people) #check if people exited; if someone was in exit, returns 1, if not, returns 0

                # Check for end conditions
                if GameBoard.num_infected() == 0:   # There are no infected people left
                    #if HUMAN_PLAY or episodes_ran % 100 == 0 or episodes_ran == episodes:
                    PF.run(GameBoard, episodes_ran)
                    PF.display_finish_screen()
                    survivors.append(GameBoard.population)
                    running = False
                
                #del oldGameboard
                
    # Store the current conditions
    epsilon_list.append(epsilon)
    survivor_list.append(sum(survivors) / len(survivors))

#print(QTable2)

print(QTable2['X']['V']['E']['E'])
#for a in possible_entries:
#    for b in possible_entries:
#        for c in possible_entries:
#            print(QTable2[a][b][c]['X'][4])

print(f"Mean # of surviving people was {sum(survivors) / len(survivors)}.")

if SHOW_EPSILON_GRAPH:
    ax.plot(epsilon_list, survivor_list)
    plt.show()
else:
    input("Press Enter to continue.")
>>>>>>> Stashed changes
