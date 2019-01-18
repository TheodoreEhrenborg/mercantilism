'''This file contains the various algorithms that play the game.
Methods starting with aux_ are not playing the game.'''
def play_highest(tokens, data, game_name):
    '''Always play the highest token left.'''
    import time
    f = open("Results/play_highest.log")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data)." + "\n")
    choice = max( tokens )
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def uniform(tokens, data, game_name):
    '''Always play a token randomly chosen based on a uniform distribution.'''
    import time, random
    f = open("Results/uniform.log")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data)." + "\n")
    choice = random.choice( tokens )
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
  
