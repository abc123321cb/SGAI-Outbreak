import csv

# data_headers = ["Board Size", "Initial Infected Pop", "Initial Human Pop", 
#                 "Turns", "Heal Moves", "Skips", "Cured", "Vaccinated", "Escaped", "Final Human Pop"]

def data_collection(HumanPlay, every_turn, GameBoard, turns_taken, AmountExited, BoardSize):
    print(every_turn)
    
    player_chose_vacc = 0
    player_chose_skip = 0
    
    for turn in every_turn:
        if "vaccinate" in turn:
            player_chose_vacc += 1
        if "pass" in turn:
            player_chose_skip += 1
    
    if BoardSize == 1:
        BoardSize = "Small"
    elif BoardSize == 2:
        BoardSize = "Medium"
    elif BoardSize == 3:
        BoardSize = "Large"
    
    print(f"The board size was {BoardSize}")
    print(f"Initial infected population: {GameBoard.infected_initial}")
    print(f"Initial human population: {GameBoard.population_initial}")
    print(f"Turns taken: {turns_taken}")
    print(f"Player chose to vaccinate or cure {player_chose_vacc} times")
    print(f"Player chose to skip the turn {player_chose_skip} times")
    print(f"Zombies cured: {GameBoard.zombies_cured}")
    print(f"Humans vaccinated: {GameBoard.humans_vaccinated}")
    print(f"Humans escaped: {AmountExited}")
    print(f"Final human population: {GameBoard.num_alive() + AmountExited}")
    
    collected_data = [BoardSize, GameBoard.infected_initial, GameBoard.population_initial, 
                    turns_taken, player_chose_vacc, player_chose_skip, GameBoard.zombies_cured, 
                    GameBoard.humans_vaccinated, AmountExited, GameBoard.num_alive() + AmountExited]
    
    if HumanPlay:
        with open("Data Collected by Humans.csv", 'a') as data_collected_humans:
            # Create the writer object
            human_writer = csv.writer(data_collected_humans)
            # Append the data
            human_writer.writerow(collected_data)
    
    elif not HumanPlay:
        with open("Data Collected by AI.csv", 'a') as data_collected_AI:
            AI_writer = csv.writer(data_collected_AI)
            AI_writer.writerow(collected_data)
    
    
def steps_taken(player_action, every_turn):
    every_turn.append(player_action)