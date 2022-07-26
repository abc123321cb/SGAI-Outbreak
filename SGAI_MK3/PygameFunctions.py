import random

import pygame
import random as rd

BACKGROUND = "#DDC2A1"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_GRAY = "#4C4E52"
GREEN = (43, 228, 98)
CELL_COLOR = (40, 40, 40)
LINE_WIDTH = 1
WIDTH, HEIGHT = 1200, 700

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Outbreak!")
pygame.font.init()
font = pygame.font.SysFont("Comic Sans", 20)
screen.fill(BACKGROUND)

# Load images
img_player_govt = None
img_player_healthy = None
img_player_vaccinated = None
img_player_infected = None

# Load menu screen surfaces and text
game_title_text = pygame.font.Font("Assets/title_font.ttf", 120)
title_surf = game_title_text.render("RESCUE!", False, RED)
title_rect = title_surf.get_rect(center = (600, 300))
menu_text = pygame.font.Font("Assets/menu_font.ttf", 40)
menu_surf = menu_text.render("Press space to begin", False, BLACK)
menu_rect = menu_surf.get_rect(center = (600, 450))
settings_surf = menu_text.render("Settings", False, BLACK)
settings_rect = settings_surf.get_rect(topright = (1150, 25))

# Load title screen background
title_background = pygame.image.load("Assets/map_background.jpeg").convert_alpha()
title_background_rect = title_background.get_rect(center = (600, 350))

# Load settings screen surfaces and text
checkmark_text = pygame.font.Font("Assets/title_font.ttf", 60)
settings_text = pygame.font.Font("Assets/menu_font.ttf", 30)

# Load and create surface for "player" setting name
player_role_surf = menu_text.render("Player", False, BLACK)
player_role_rect = player_role_surf.get_rect(center = (300, 200))

# Load and create surfaces for "player" options (AI Model or Human Play)
AI_surf = settings_text.render("AI Model", False, BLACK)
AI_rect = AI_surf.get_rect(center = (900, 200))
AI_box = pygame.Rect(AI_rect.x - 30, 190, 20, 20)
human_surf = settings_text.render("Human Player", False, BLACK)
human_rect = human_surf.get_rect(center = (900 - AI_rect.width - 100, 200))
human_box = pygame.Rect(human_rect.x - 30, 190, 20, 20)

# Load selected setting visual that can be changed by user input
checkmark_text = checkmark_text.render("X", False, RED)
AI_text_rect = checkmark_text.get_rect(center = (WIDTH - 265 - AI_rect.width, 205))
human_text_rect = checkmark_text.get_rect(center = (human_rect.x - 20, 205))

# Load surface to return to title page
back_surf = menu_text.render("Back", False, BLACK)
back_rect = back_surf.get_rect(topleft = (50, 25))

# Load surfaces for "gameboard size" setting
gameboard_change_surf = menu_text.render("Gameboard Size", False, BLACK)
gameboard_change_rect = gameboard_change_surf.get_rect(center = (300, 300))
small_surf = settings_text.render("Small", False, BLACK)
small_rect = small_surf.get_rect(center = ((AI_rect.x + human_rect.x)//2 - 125, 300))
small_box = pygame.Rect(small_rect.x - 30, 290, 20, 20)
small_text_rect = checkmark_text.get_rect(topleft = (small_rect.x - 42, 255))

medium_surf = settings_text.render("Medium", False, BLACK)
medium_rect = medium_surf.get_rect(center = (small_rect.x + 200, 300))
medium_box = pygame.Rect(medium_rect.x - 30, 290, 20, 20)
medium_text_rect = checkmark_text.get_rect(topleft = (medium_rect.x - 42, 255))

large_surf = settings_text.render("Large", False, BLACK)
large_rect = large_surf.get_rect(center = (medium_rect.x + 200, 300))
large_box = pygame.Rect(large_rect.x - 30, 290, 20, 20)
large_text_rect = checkmark_text.get_rect(topleft = (large_rect.x - 42, 255))


def load_images(GameBoard):
    """
    Load all of the game image assets once
    Only blit these on refresh, instead of loading them each time
    TODO: find a way to implement this without using the global method here...
    """
    global img_player_govt
    global img_player_healthy
    global img_player_vaccinated
    global img_player_infected

    img_player_size = (int(0.8 * GameBoard.cell_size / 2), int(0.8 * GameBoard.cell_size))
    img_player_govt = pygame.image.load("Assets/person_govt.png").convert_alpha()
    img_player_govt = pygame.transform.scale(img_player_govt, img_player_size)
    img_player_healthy = pygame.image.load("Assets/person_normal.png").convert_alpha()
    img_player_healthy = pygame.transform.scale(img_player_healthy, img_player_size)
    img_player_vaccinated = pygame.image.load("Assets/person_vax.png").convert_alpha()
    img_player_vaccinated = pygame.transform.scale(img_player_vaccinated, img_player_size)
    img_player_infected = pygame.image.load("Assets/person_infect.png").convert_alpha()
    img_player_infected = pygame.transform.scale(img_player_infected, img_player_size)


def get_grid_clicked(GameBoard, pixel_x, pixel_y):
    """
    Get the action that the click represents.
    If the click was on the heal button, returns "heal"
    Else, returns the board coordinates of the click (board_x, board_y) if valid
    Return False otherwise
    """
    # Get the grid (x,y) where the user clicked
    if pixel_x > GameBoard.offset and pixel_y > GameBoard.offset:   # Make sure the click is not to the left or top of the grid
        board_x = int((pixel_x - GameBoard.offset) / GameBoard.cell_size)
        board_y = int((pixel_y - GameBoard.offset) / GameBoard.cell_size)
        # Return the grid position if it is a valid position on the board
        if (board_x >= 0 and board_x < GameBoard.columns and board_y >= 0 and board_y < GameBoard.rows):
            return (board_x, board_y)
    return False


def get_possible_moves(GameBoard, player_coor, include_vaccinate):
    """
    Return a list of all possible moves that the player is allowed to take from the current position.
    Check if the move direction is in bounds
    If so, check if the space is empty.
    If the space is empty, then add the ["move",direction] to the list.
    If include_vaccinate is True, then also check if vaccination is an option. 
    If the space is not empty AND the person is not vaccinated, then add the ["vaccinate",direction] to the list.
    """
    possible_moves = []
    possible_moves.append(["pass"])
    if player_coor[0] > 0:
        if GameBoard.state[GameBoard.toIndex([player_coor[0] - 1, player_coor[1]])] == None:
            possible_moves.append(["move", "left"])
        elif include_vaccinate:
            if not GameBoard.state[GameBoard.toIndex([player_coor[0] - 1, player_coor[1]])].isVaccinated:
                possible_moves.append(["vaccinate", "left"])
    if player_coor[0] < (GameBoard.columns - 1):
        if GameBoard.state[GameBoard.toIndex([player_coor[0] + 1, player_coor[1]])] == None:
            possible_moves.append(["move", "right"])
        elif include_vaccinate:
            if not GameBoard.state[GameBoard.toIndex([player_coor[0] + 1, player_coor[1]])].isVaccinated:
                possible_moves.append(["vaccinate", "right"])
    if player_coor[1] > 0:
        if GameBoard.state[GameBoard.toIndex([player_coor[0], player_coor[1] - 1])] == None:
            possible_moves.append(["move", "up"])
        elif include_vaccinate:
            if not GameBoard.state[GameBoard.toIndex([player_coor[0], player_coor[1] - 1])].isVaccinated:
                possible_moves.append(["vaccinate", "up"])
    if player_coor[1] < (GameBoard.rows - 1):
        if GameBoard.state[GameBoard.toIndex([player_coor[0], player_coor[1] + 1])] == None:
            possible_moves.append(["move", "down"])
        elif include_vaccinate:
            if not GameBoard.state[GameBoard.toIndex([player_coor[0], player_coor[1] + 1])].isVaccinated:
                possible_moves.append(["vaccinate", "down"])
    return possible_moves


def run(GameBoard, exitpoints, amount_exited, episodes_ran = False):
    """
    Draw the screen and return any events.
    """
    screen.fill(BACKGROUND)
    build_grid(GameBoard) # Draw the grid
    display_people(GameBoard, exitpoints)
    display_stats(GameBoard, amount_exited, episodes_ran)


def build_grid(GameBoard):
    """
    Draw the grid on the screen.
    """
    grid_width = GameBoard.columns * GameBoard.cell_size
    grid_height = GameBoard.rows * GameBoard.cell_size
    pygame.draw.rect(screen, BLACK, [GameBoard.offset - LINE_WIDTH, GameBoard.offset - LINE_WIDTH, LINE_WIDTH, grid_height + (2 * LINE_WIDTH)])  # left
    pygame.draw.rect(screen, BLACK, [GameBoard.offset + grid_width, GameBoard.offset - LINE_WIDTH, LINE_WIDTH, grid_height + (2 * LINE_WIDTH)])  # right
    pygame.draw.rect(screen, BLACK, [GameBoard.offset - LINE_WIDTH, GameBoard.offset + grid_height, grid_width + (2 * LINE_WIDTH), LINE_WIDTH])  # bottom
    pygame.draw.rect(screen, BLACK, [GameBoard.offset - LINE_WIDTH, GameBoard.offset - LINE_WIDTH, grid_width + (2 * LINE_WIDTH), LINE_WIDTH])   # top
    pygame.draw.rect(screen, CELL_COLOR, [GameBoard.offset, GameBoard.offset, grid_width, grid_height]) # Fill the inside wioth the cell color
    # Draw the vertical lines
    i = GameBoard.offset + GameBoard.cell_size
    while i < GameBoard.offset + grid_width:
        pygame.draw.rect(screen, BLACK, [i, GameBoard.offset, LINE_WIDTH, grid_height])
        i += GameBoard.cell_size
    # Draw the horizontal lines
    i = GameBoard.offset + GameBoard.cell_size
    while i < GameBoard.offset + grid_height:
        pygame.draw.rect(screen, BLACK, [GameBoard.offset, i, grid_width, LINE_WIDTH])
        i += GameBoard.cell_size


def display_people(GameBoard, exitpoints):
    """
    Draw the people on the screen.
    """
    for exits in exitpoints:
        curr_coor = GameBoard.toCoord(exits.location)
        pygame.draw.rect(screen, GREEN, [GameBoard.offset + curr_coor[0] * GameBoard.cell_size,
                                         GameBoard.offset + curr_coor[1] * GameBoard.cell_size, GameBoard.cell_size,
                                         GameBoard.cell_size])
    for person in GameBoard.people:
        if person != None:
            coords = (
                GameBoard.toCoord(person.location)[0] * GameBoard.cell_size + GameBoard.offset + 0.3 * GameBoard.cell_size,
                GameBoard.toCoord(person.location)[1] * GameBoard.cell_size + GameBoard.offset + 0.1 * GameBoard.cell_size
            )
            if person.isGovt:
                curr_coor = GameBoard.toCoord(person.location)
                pygame.draw.rect(screen, WHITE, [
                    GameBoard.offset + curr_coor[0] * GameBoard.cell_size, GameBoard.offset + curr_coor[1] * GameBoard.cell_size, GameBoard.cell_size, GameBoard.cell_size])
                screen.blit(img_player_govt, coords)
            elif person.condition == "Healthy":
                screen.blit(img_player_healthy, coords)
            elif person.condition == "Cured":
                screen.blit(img_player_vaccinated, coords)
            else: # only infected people right now
                screen.blit(img_player_infected, coords)


def simulate(GameBoard):
    """
    Allow all the non-government people in the simulation to take a turn.
    """
    for person in GameBoard.people:
        if person != None:
            if not person.isGovt:
                # Get the person's location
                player_loc = GameBoard.toCoord(person.location)
                
                # If the person is infected, then potentially infect any adjacent people
                if person.isInfected:
                    uninfected_index = GameBoard.adjacent_noninfected_index(player_loc)
                    for uninfected_person in uninfected_index:
                        if rd.randint(0,100) < person.infectiousAmount:
                            GameBoard.state[uninfected_person].infect_person()
                
                # Choose a possible move and perform it
                possible_moves = get_possible_moves(GameBoard, player_loc, False)
                if len(possible_moves) > 0:
                    this_move = rd.choice(possible_moves)
                    if this_move[0] == "move":
                        GameBoard.move(this_move[1], player_loc, False)


def progress_infection(GameBoard, days_to_death):
    """
    Progress infection counts on infected people.
    Some people will die as infection continues.
    """
    for person in GameBoard.people:
        if person != None:
            if person.isInfected:
                person.daysInfected += 1
                chance = int( (rd.randint(0,100) * (1 - (person.daysInfected / days_to_death))) )
                if chance < 1:
                    GameBoard.death(person.location, person.index)


def display_stats(GameBoard, amount_exited, episodes_ran):
    if episodes_ran:
        screen.blit(font.render(f"Episode Number: {episodes_ran}", True, WHITE), (800, 375))
    screen.blit(font.render(f"Initial population: {GameBoard.population_initial}", True, WHITE), (800, 400))
    screen.blit(font.render(f"Current population: {GameBoard.population}", True, WHITE), (800, 425))
    screen.blit(font.render(f"Total infected: {GameBoard.num_infected()}", True, WHITE), (800, 450))
    screen.blit(font.render(f"Total vaccinated: {GameBoard.num_vaccinated()}", True, WHITE), (800, 475))
    screen.blit(font.render(f"Total escaped: {amount_exited}", True, WHITE), (800, 500))

def display_finish_screen():
    screen.blit(font.render("SIMULATION OVER.", True, WHITE), (800, 300))
    pygame.display.update()


def reward(old_board, new_board, action):
    """
    This is the all important reward function.
    """
    # The default reward is -1
    reward = -1
    
    # Reward for vaccinating this turn
    if action[0] == "vaccinate":
        reward = 10
    
    # Return for having less infected people
    #reward += old_board.num_infected() - new_board.num_infected()
    
    # Negative reward if the population goes down
    #reward -= 3 * (new_board.population_initial - new_board.population - old_board.population_initial + old_board.population)
    
    return reward

def reward2(action, GameBoard):
    reward = -1
    if action[0] == "vaccinate":
        reward = 100
    #reward -= GameBoard.num_infected() + 2 * (GameBoard.population - GameBoard.population_initial)

    return reward


def convert_to_action(num):
    """
    Take a numerical action and returns the correspodning action as a string.
    Returns False if not valid.
    """
    # First get the type of action
    if num < 4:     # 0,1,2,3
        this_action = ["vaccinate"]
    elif num < 8:    # 4,5,6,7
        this_action = ["move"]
    
    # Now add the direction
    if num == 0 or num == 4:
        this_action.append("left")
    elif num == 1 or num == 5:
        this_action.append("right")
    elif num == 2 or num == 6:
        this_action.append("up")
    elif num == 3 or num == 7:
        this_action.append("down")
    
    return this_action

def greedy_epsilon(epsilon, QTable_at_curr_position):
    """
    Implements the greedy epsilon algorithm to choose which action to take next.
    """
    if random.random() > float(epsilon):
        max_Q = random.choice(QTable_at_curr_position)
    else:
        max_Q = max(QTable_at_curr_position)
    choice = QTable_at_curr_position.index(max_Q)
    return convert_to_action(choice), choice

def update_Q_value(old_Q, learn, reward, discount_factor, max_new_Q):
    """
    Calculates the Q value to update the Q Table.
    Temporal difference = reward + (discount_factor * Max Q value at new location) - Old Q-value
    New Q-value = Old Q-value + (learning_rate * temporal difference)
    """
    temporal_difference = reward + (discount_factor * max_new_Q) - old_Q
    return old_Q + (learn * temporal_difference)

def main_screen():
    screen.blit(title_background, title_background_rect)
    screen.blit(title_surf, title_rect)
    screen.blit(menu_surf, menu_rect)
    screen.blit(settings_surf, settings_rect)
    
    pygame.display.update()
    
    
def settings_screen(HUMAN_PLAY, BOARD_SIZE):
    screen.blit(title_background, title_background_rect)
    screen.blit(player_role_surf, player_role_rect)
    screen.blit(human_surf, human_rect)
    screen.blit(AI_surf, AI_rect)
    pygame.draw.rect(screen, DARK_GRAY, AI_box, 3)
    pygame.draw.rect(screen, DARK_GRAY, human_box, 3)
    screen.blit(back_surf, back_rect)
    screen.blit(gameboard_change_surf, gameboard_change_rect)
    screen.blit(small_surf, small_rect)
    pygame.draw.rect(screen, DARK_GRAY, small_box, 3)
    screen.blit(medium_surf, medium_rect)
    pygame.draw.rect(screen, DARK_GRAY, medium_box, 3)
    screen.blit(large_surf, large_rect)
    pygame.draw.rect(screen, DARK_GRAY, large_box, 3)
    
    if HUMAN_PLAY:
        screen.blit(checkmark_text, human_text_rect)
    else:
        screen.blit(checkmark_text, AI_text_rect)
        
    if BOARD_SIZE == 1:
        screen.blit(checkmark_text, small_text_rect)
    elif BOARD_SIZE == 2:
        screen.blit(checkmark_text, medium_text_rect)
    elif BOARD_SIZE == 3:
        screen.blit(checkmark_text, large_text_rect)
    
    pygame.display.update()