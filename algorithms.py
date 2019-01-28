'''This file contains the various algorithms that play the game.
Methods starting with aux_ are not playing the game.'''
def play_highest(tokens, data, game_name):
    '''Plays the highest token left.'''
    import time
    f = open("Results/play_highest.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) + ". \n")
    choice = max( tokens )
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def uniform(tokens, data, game_name):
    '''Plays a token randomly, chosen based on a uniform distribution.'''
    import time, random
    f = open("Results/uniform.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) + ". \n")
    choice = random.choice( tokens )
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def aux_exp(tokens, data, game_name, n):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to n^(value) '''
    import time, random
    f = open("Results/exp.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) +  ". n = "  + str(n) + "\n")
    sum = 0
    for x in tokens:
        sum += n**x
    random_choice = random.random() * sum
    for x in tokens:
        random_choice -= n**x
        if random_choice < 0:
            break
    else:
        raise Exception("Uh-oh. The program should never reach this step.")
    choice = x
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def exp_2(tokens, data, game_name):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to 2^(value) '''
    return aux_exp(tokens, data, game_name, 2)
def aux_power(tokens, data, game_name, n):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to (value)^n '''
    import time, random
    f = open("Results/power.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) +  ". n = "  + str(n) + "\n")
    sum = 0
    for x in tokens:
        sum += x**n
    random_choice = random.random() * sum
    for x in tokens:
        random_choice -= x**n
        if random_choice < 0:
            break
    else:
        raise Exception("Uh-oh. The program should never reach this step.")
    choice = x
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def power_2(tokens, data, game_name):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to (value)^2 '''
    return aux_power(tokens, data, game_name, 2)
def power_1(tokens, data, game_name):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to its value'''
    return aux_power(tokens, data, game_name, 1)
def best_human(tokens, data, game_name):
    '''Pick a number (one-third chance it's 2nd highest, one-third 3rd highest,
    one-third 4th highest). But if it is in first place and my score - 2nd place score
    >= highest token left, I pick the highest value token.'''
    import random
    l = len(tokens)
    tokens.sort().reverse()
    choices = []
    for i in range( len( tokens) ):
        if i in [1,2,3]:
            choices.append(tokens[i])
    if choices == []:
        choices.append(tokens[0])#If there is no second choice, there must be just one token
    default = random.choice( choices )
    
      
