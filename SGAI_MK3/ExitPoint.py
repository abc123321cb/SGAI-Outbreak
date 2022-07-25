class ExitPoint:
    def __init__(self, this_index, location):
        self.index = this_index #assigning it an index in case we want multiple exit points in future
        self.location = location #assigning location; exit point does not need 'conditions'
    
    def CheckPeopleExited(self, PersonSet, GameBoard):
        Amount = 0 #setting a counter of people who have exited
        for Person in PersonSet: #iterating through each person in the set
            if Person.location == self.location and Person.isInfected != True: #check if they're not infected and are in the exit point
                Amount += 1 #add to counter
                GameBoard.Death(Person.location, Person.index) #"death" event to remove them from board
                return Amount #return the amount
                #only one person can be at the tile at once, so 
        return Amount #return the amount
 


            
    

