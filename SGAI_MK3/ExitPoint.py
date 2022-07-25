class ExitPoint:
    def __init__(self, location):
        #self.index index not necessary currently? all it needs is location
        self.location = location #assigning location; exit point does not need 'conditions'
    
    def CheckPeopleExited(self, PersonSet, GameBoard):
        PersonExited = 0 #setting a counter of people who have exited
        for Person in PersonSet: #iterating through each person in the set
            if Person != None and Person.location == self.location and Person.isInfected != True: #check if they're not infected and are in the exit point
                PersonExited += 1 #add to counter
                GameBoard.death(Person.location, Person.index) #"death" event to remove them from board
                return PersonExited #return the amount, early return since no one else could be in the tile
                #only one person can be at the tile at once, so there is no need to remove it 
        return PersonExited #return the amount