import random as rd
from unittest.mock import NonCallableMagicMock
from Person import Person
import numpy

class Board:
    """
    Stores the game board.
    """
    
    def __init__(self, dimensions, offset, cell_size, role):
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        self.offset = offset
        self.cell_size = cell_size
        self.govt_index = None
        self.player_role = role
        self.population = 0
        self.zombies_cured = 0
        self.humans_vaccinated = 0
        self.people = []    # stores a list of all people (healthy and infected)
        self.state = []     # stores the current inhabitant of each location (in 1D index)
        for s in range(self.rows * self.columns):
            self.state.append(None)

    def num_infected(self):
        """
        Returns the number of infected people currently on the board.
        """
        infected_count = 0
        for person in self.people:
            if person != None:
                if person.isInfected:
                    infected_count += 1
        return infected_count
    
    def num_vaccinated(self):
        """
        Returns the number of vaccinated people currently on the board.
        """
        vaccinated_count = 0
        for person in self.people:
            if person != None:
                if person.isVaccinated:
                    vaccinated_count += 1
        return vaccinated_count
    
    def num_alive(self):
        """
        Returns the number of alive people (regardless of vaccination status) currently on the board.
        """
        alive_count = 0
        for person in self.people:
            if person != None:
                if person.isInfected:
                    pass
                else:
                    alive_count += 1
        return alive_count
    
    def toCoord(self, index):
        return (index % self.columns, int(index / self.columns))

    def toIndex(self, coordinates):
        return int(coordinates[1] * self.columns) + int(coordinates[0])

    def isValidCoordinate(self, coordinates):
        return (
            coordinates[1] < self.rows
            and coordinates[1] >= 0
            and coordinates[0] < self.columns
            and coordinates[0] >= 0)

    def isAdjacentTo(self, coord, is_infected: bool):
        ret = False
        vals = [
            (coord[0], coord[1] + 1),
            (coord[0], coord[1] - 1),
            (coord[0] + 1, coord[1]),
            (coord[0] - 1, coord[1]),
        ]
        for coord in vals:
            if self.isValidCoordinate(coord):
                if self.state[self.toIndex(coord)] is not None:
                    if self.state[self.toIndex(coord)].isInfected == is_infected:
                        ret = True
                        break

        return ret
    
    def adjacent_noninfected_index(self, player_loc):
        vals = [
            [player_loc[0],     player_loc[1] + 1],
            [player_loc[0],     player_loc[1] - 1],
            [player_loc[0] + 1, player_loc[1]    ],
            [player_loc[0] - 1, player_loc[1]    ],
        ]
        adj_coord = []
        for coord in vals:
            if self.isValidCoordinate(coord):
                if self.state[self.toIndex(coord)] is not None:                     # a person is here
                    if not self.state[self.toIndex(coord)].isInfected:              # the person is not infected
                        if not self.state[self.toIndex(coord)].isGovt:              # the person is not the player
                            if not self.state[self.toIndex(coord)].isVaccinated:    # the person is not vaccinated
                                adj_coord.append(self.toIndex(coord))
        return adj_coord
    
    def get_coor(self, direction, old_coor):
        """
        Returns the coordinate adjusted for the provided direction.
        """
        new_coor = False
        if direction == "up":
            new_coor = [old_coor[0], old_coor[1] - 1]
        elif direction == "down":
            new_coor = [old_coor[0], old_coor[1] + 1]
        elif direction == "left":
            new_coor = [old_coor[0] - 1, old_coor[1]]
        elif direction == "right":
            new_coor = [old_coor[0] + 1, old_coor[1]]
        return new_coor
    
    def move(self, direction, player_loc, is_govt):
        """
        Moves the player.
        Assumes the position sent is valid.
        If is_govt, then also set the new position of the user-playable player
        """
        # Get the new coordinate to move
        old_index = self.toIndex(player_loc)
        new_index = self.toIndex(self.get_coor(direction, player_loc))
        
        # Move the player and set attributes
        self.state[old_index].location = new_index                                                  # Set the new location for the player
        self.state[old_index], self.state[new_index] = self.state[new_index], self.state[old_index] # Swap the state positions
        
        if is_govt:
            self.govt_index = new_index                                                                 # Point to the new position of the player
    
    def vaccinate(self, direction, player_loc):
        """
        Vaccinates the person at the stated coordinates.
        Assumes the position and people status sent is valid.
        """
        # Get the new coordinate to heal
        new_index = self.toIndex(self.get_coor(direction, player_loc))
        
        # Store whether a human was vaccinated or a zombie was cured
        person_healed = self.state[new_index]
        if person_healed.isInfected:
            self.zombies_cured += 1
        else:
            self.humans_vaccinated += 1
            
        # Heal the person
        self.state[new_index].heal_person()
    
    def death(self, location, index):
        """
        Kill the person.
        """
        #person = self.state[index]
        self.state[location] = None
        self.people[index] = None
        self.population -= 1
        
    def populate(self):
        """
        Populate the board with people.
        Clears the existing state list and people list
        """
        
        # Clear the board and player list
        self.state = []
        for s in range(self.rows * self.columns):
            self.state.append(None)
        self.people = []
        
        # Determine how many people to create
        target_population_size = rd.randint(int((self.rows * self.columns) / 4), int((self.rows * self.columns) / 3))
        
        # Make a list of unique positions to add healthy people
        location_healthy_set = set()    # Use a set for placing people because duplicates will automatically be deleted.
        while len(location_healthy_set) < target_population_size:
            selected_index = rd.randint(0, int(self.rows * self.columns) - 1)
            location_healthy_set.add(selected_index)
        
        # Add healthy people to each of the unique positions
        for index in location_healthy_set:
            this_healthy_person = Person(len(self.people), "Healthy", index)
            self.people.append( this_healthy_person )
            self.state[index] = this_healthy_person

        # Make a list of some of the created people to change them to "Infected" at random
        location_infected_set = set()
        while len(location_infected_set) < 4:    # Four is an arbitrary number
            selected_index = rd.choice(list(location_healthy_set))  # Have to convert the set to a list in order to select with rd.choice
            location_infected_set.add(selected_index)
            location_healthy_set.remove(selected_index)
        
        # Change the person to infected
        for index in location_infected_set:
            self.state[index].infect_person()
        
        # Set the population attribute
        self.population = len(location_healthy_set)
        self.population_initial = self.population
        
        # Set the infected attribute
        self.infected_initial = len(location_infected_set)
        
        # Make a list of one of the created healthy people to change them to "Govt" at random
        govt_index_found = False
        while not govt_index_found: 
            selected_index = rd.choice(list(location_healthy_set))  # Have to convert the set to a list in order to select with rd.choice
            if selected_index not in location_infected_set:
                govt_index_found = True
        
        # Change the person to government
        self.govt_index = selected_index
        self.state[selected_index].isGovt = True
    
    def state_contents_to_char(self, state_contents):
        """
        Returns the character representation for a particular state position.
            'V' = a vaccinated person is in the location
            'U' = an unvaccinated person is in the location
            'X' = a boundary of the grid is in the location
            'I' = an infected person is in the location
            'E' = the space is empty
        """
        if state_contents == None:
            return "E"
        elif state_contents.isInfected:
            return "I"
        elif state_contents.isVaccinated:
            return "V"
        else:
            return "U"
    
    def sense_nearby(self):
        """
        Checks the found positions next to the government player and returns the contents.
        returns a list with the contents in the order of up, right, down, left
        """
        nearby_contents = []
        player_loc = self.toCoord(self.state[self.govt_index].location)
        
        # Look up
        if player_loc[1] == 0:
            nearby_contents.append('X')
        else:
            this_contents = self.state[self.toIndex([player_loc[0], player_loc[1] - 1])]
            nearby_contents.append(self.state_contents_to_char(this_contents))
        
        # Look right
        if player_loc[0] == (self.columns - 1):
            nearby_contents.append('X')
        else:
            this_contents = self.state[self.toIndex([player_loc[0] + 1, player_loc[1]])]
            nearby_contents.append(self.state_contents_to_char(this_contents))
        
        # Look down
        if player_loc[1] == (self.rows - 1):
            nearby_contents.append('X')
        else:
            this_contents = self.state[self.toIndex([player_loc[0], player_loc[1] + 1])]
            nearby_contents.append(self.state_contents_to_char(this_contents))
        
        # Look left
        if player_loc[0] == 0:
            nearby_contents.append('X')
        else:
            this_contents = self.state[self.toIndex([player_loc[0] - 1, player_loc[1]])]
            nearby_contents.append(self.state_contents_to_char(this_contents))
        
        return nearby_contents
    
    def state_map(self):
        """
        Create a 2D state map for the deep Q Learning algorithm to learn from.
        """
        new_state = numpy.zeros((self.columns, self.rows))
        this_y = -1
        for this_index, this_content in enumerate(self.state):
            if (this_index % self.columns) == 0:
                this_y += 1
            new_state[this_index % self.columns][this_y] = ord(self.state_contents_to_char(this_content))
        return new_state