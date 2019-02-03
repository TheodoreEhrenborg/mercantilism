'''This file contains the various algorithms that play the game.
Methods starting with aux_ are not playing the game.'''
TOKENS = range(1,16)
NUM_PLAYERS = 5
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
def power_3(tokens, data, game_name):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to (value)^3 '''
    return aux_power(tokens, data, game_name, 3)
def power_2(tokens, data, game_name):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to (value)^2 '''
    return aux_power(tokens, data, game_name, 2)
def power_1(tokens, data, game_name):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to its value'''
    return aux_power(tokens, data, game_name, 1)
def best_human_strategy(tokens, data, game_name):
    '''Pick a number (one-third chance it's 2nd highest, one-third 3rd highest,
    one-third 4th highest). But if I am in first place and my score - 2nd place score
    >= highest token left, I pick the highest value token.'''
    import random, time
    f = open("Results/best_human_strategy.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) + ". \n")
    l = len(tokens)
    tokens.sort()
    tokens.reverse()
    choices = []
    for i in range( len( tokens) ):
        if i in [1,2,3]:
            choices.append(tokens[i])
    if choices == []:
        choices.append(tokens[0])#If there is no second choice, there must be just one token
    default = random.choice( choices )
    #The first entry in data is this player
    my_score = data[0][0]
    highest = True
    highest_other_score = 0
    for other in data[1:]:
        if other[0] >  highest_other_score:
            highest_other_score = other[0]
    if my_score - highest_other_score >= tokens[0]: #In this case there's no harm in choosing the highest token.
        f.write(time.asctime() + ": Chose the highest token: " + str(tokens[0]) + "\n")
        f.close()
        return tokens[0]
    else:
        f.write(time.asctime() + ": Chose a default: " + str(default) + "\n")
        f.close()
        return default
def quick_evolve(tokens, data, game_name):
    q = Quick_Evolver()
    return q.choose_token( tokens, data, game_name )
class Quick_Evolver:
    '''Makes a decision by choosing one of the fast algorithms'''
    fast_algorithms = ( play_highest, uniform, exp_2, power_1, power_2, power_3, best_human_strategy)
    @classmethod
    def list_add(cls, a, b):
        c = []
        if len(a) != len(b):
            raise Exception( str( ( len(a), len(b) ) ) )
        for i in range(len(a)):
            c.append( a[i] + b[i] )
        return c
    @classmethod
    def evolve(cls, generations = 5 , trials_per_generation = 100, mutation_size = 0.1, mutation_number = 1):
        import copy
        for gen in range(generations):
            players = []
            scores = []
            parent = Quick_Evolver()
            players.append(parent)
            scores.append(0)
            for i in range(NUM_PLAYERS - 1):
                p = Quick_Evolver()
                p.mutate(how_many = mutation_number, how_far = mutation_size)
                players.append(p)
                scores.append(0)
            #Now play games and choose the best player
            for trial in range(trials_per_generation):
                g = Game( copy.copy(players), copy.copy(TOKENS) )
                scores = cls.list_add( g.get_results(), scores)
            max_score = max(scores)
            i = scores.index(max_score)
            best = players[i]
            best.become_parent()
        return best
    def __init__(self, return_to_default = False):
        try:
            f = open("Results/quick_evolver_settings.txt", "r")
        except IOError:
            self.weights = []
            for x in range(len(Quick_Evolver.fast_algorithms)):
                self.weights.append(1)
            f = open("Results/quick_evolver_settings.txt", "w")
            f.write(str(self.weights))
            f.close()
        else:
            self.weights = eval( f.read() )
            f.close()
        if return_to_default:
            self.weights = []
            for x in range(len(Quick_Evolver.fast_algorithms)):
                self.weights.append(1)
    def choose_token( self, tokens, data, game_name):
        return self.choose_algorithm()(tokens, data, game_name)
    def choose_algorithm( self):
        '''Given the current information, makes a decision about what algorithm to use'''
        import random
        sum = 0
        for x in self.weights:
            sum += x
        random_choice = random.random() * sum
        for i in range(len(self.weights)):
            random_choice -= self.weights[i]
            if random_choice < 0:
                break
        else:
            raise Exception("Uh-oh. The program should never reach this step.")
        return Quick_Evolver.fast_algorithms[i]
    def become_parent(self):
        f = open("Results/quick_evolver_settings.txt", "w")
        f.write(str(self.weights))
        f.close()
    def mutate(self, how_many = 1, how_far = 0.1):
        import random
        how_far = abs(how_far)
        l = len(self.weights)
        for x in range(how_many):
            r = random.randrange(l)
            value = self.weights[r]
            if value < how_far:
                self.weights[r] += how_far
            elif random.random() < 0.5:
                self.weights[r] += how_far
            else:
                self.weights[r] -= how_far
    def __str__(self):
        return "Quick_Evolver: Weights are " + str(self.weights)
    def __repr__(self):
        return str(self)
class Neural_Evolver:
    '''Makes a decision using a neural setwork trained through artificial selection'''
    @classmethod
    def list_add(cls, a, b):
        c = []
        if len(a) != len(b):
            raise Exception( str( ( len(a), len(b) ) ) )
        for i in range(len(a)):
            c.append( a[i] + b[i] )
        return c
    @classmethod
    def list_multiply(cls, a, b):
        c = []
        if len(a) != len(b):
            raise Exception( str( ( len(a), len(b) ) ) )
        for i in range(len(a)):
            c.append( a[i] * b[i] )
        return c
    @classmethod
    def list_total(cls, a):
        total = 0
        for x in a:
            total += x
        return total
    @classmethod
    def evolve(cls, generations = 5 , trials_per_generation = 100, mutation_size = 0.1, mutation_chance = 0.2):
        import copy,time
        players = []
        for i in range(NUM_PLAYERS):
            p = Neural_Evolver()
            players.append(p)
        gen = 0
        while gen < generations:
            gen += 1
            t = time.time()
            scores = []
            for i in range(NUM_PLAYERS):
                p = players[i]
                p.load()
                if i > 0:
                    p.mutate(chance = mutation_chance, how_far = mutation_size)
                scores.append(0)
            #Now play games and choose the best player
            for trial in range(trials_per_generation):
#                g = Game( copy.copy(players), copy.copy(TOKENS) )
                g = Game( players, copy.copy(TOKENS) )
                scores = cls.list_add( g.get_results(), scores)
            max_score = max(scores)
            i = scores.index(max_score)
            best = players[i]
            best.become_parent()
            print max_score / (trials_per_generation), time.time() - t
#            clear_session()
#            for p in players:
#                p.delete()
#            print best
#        return best.model.get_weights()[0][0]
#        return max_score / (trials_per_generation)
    def __init__(self, return_to_default = False):
#        try:
##            import tensorflow.keras
#            from tensorflow.keras.models import load_model
#            self.model = load_model('Results/current_model.h5')
        try:
            self.model = self.get_standard_model()
            self.load()
        except IOError:#Is this the right error?
            self.model = self.get_standard_model()
            self.become_parent()
        if return_to_default:
            self.model = self.get_standard_model()
    def load(self):
        import pickle
        f = open("Results/current_model.p","rb")
        self.model.set_weights(pickle.load(f))
    def choose_token( self, tokens, data, game_name):
        import collections,random
        import numpy as np
        scores = []
        for item in data:
            scores.append( float(item[0]) / Neural_Evolver.list_total(TOKENS) )
        if tokens == []:
            print "tokens == []"
        c = collections.Counter(tokens)
        existing_tokens = []
        for i in range(1,16):
            existing_tokens.append( c[i] )
        l = len( existing_tokens ) + len( scores )
        the_input = np.array( existing_tokens + scores)
        the_input.shape = (1,l)
        #print the_input
        output = self.model.predict( the_input )
        #print output
        weights = list(output[0])
#        print weights
        zeroed_weights = []
        for i in range(len(TOKENS)):
            t = TOKENS[i]
            zeroed_weights.append( weights[i]  * c[t] )
#        zeroed_weights = Neural_Evolver.list_multiply(list(output[0]),c)
#        print zeroed_weights
        if Neural_Evolver.list_total(zeroed_weights) == 0:
#            print weights, zeroed_weights
            choice = random.choice( tokens )
        else:
            choice = self.get_token_from_weights(zeroed_weights)
        return choice
    def delete(self):
        from tensorflow.keras.backend import clear_session
        clear_session()
        print self.model
    def get_token_from_weights(self, weights):
        import random
#        weights.shape = (1,)
        sum = Neural_Evolver.list_total(weights)
        random_choice = random.random() * sum
        for i in range(len(weights)):
            random_choice -= weights[i]
            if random_choice < 0:
                break
        else:
            raise Exception("Uh-oh. The program should never reach this step." + str(random_choice) + str(weights))
        return i + 1
    def get_standard_model(self):
 #       import tensorflow.keras
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Activation
        from tensorflow.keras.optimizers import SGD
        model = Sequential()
        model.add(Dense(30, activation='relu', input_dim=20) )
        model.add(Dense(30, activation='relu'))
        model.add(Dense(15, activation='softmax'))
        model.compile(optimizer='rmsprop',
          loss='categorical_crossentropy',
          metrics=['accuracy'])#These terms don't have any significance
        return model
    def old_become_parent(self):
        import os
        os.system("rm -f Results/current_model.h5")
        self.model.save("Results/current_model.h5")
    def become_parent(self):
        import os,pickle
        os.system("rm -f Results/current_model.p")
        f = open("Results/current_model.p","wb")
        pickle.dump( self.model.get_weights(), f)
        f.close()
    def mutate(self, chance = 0.2, how_far = 0.1):
        import random,numpy
        how_far = abs(how_far)
        weights = self.model.get_weights()
        for i in range(len(weights)):
            ww = weights[i]
            for j in range(len(ww)):
                if type(ww[j]) == numpy.float32:
                    if random.random() < chance:
                        if random.random() < 0.5:
                            weights[i][j] += how_far
                        else:
                            weights[i][j] -= how_far
                else:
                    www = ww[j]
                    for k in range(len(www)):
                        if random.random() < chance:
                            if random.random() < 0.5:
                                weights[i][j][k] += how_far
                            else:
                                weights[i][j][k] -= how_far
        self.model.set_weights( weights )
#    def __str__(self):
#        return "Neural_Evolver: Weights are " + str(self.model.get_weights())
    def __str__(self):
        return "Neural_Evolver"
    def __repr__(self):
        return "Neural_Evolver"
class Game:
    '''This version of game assumes that the algorithms are objects, not functions'''
    def get_results(self):
        return tuple( self.results )
    def __init__(self, algorithm_tuple, tokens):
        import random, collections, copy, time
        '''Calculates a list containing the utility points of
        each player'''
        self.start_time = time.time()
        self.tokens = list(tokens)
        self.algorithm_list = []
        #Each element of this list is itself a list containing the algorithm, its current score, and
        #a list (where elements with larger indexes are later) of this algorithm's moves.
        for x in algorithm_tuple:
            self.algorithm_list.append( [ x, 0, [] ] )
        self.algorithm_tuple = algorithm_tuple
        self.name = str(int( time.time() )) + ":" + str(random.randint(0,10**9))
        #Each algorithm receives a list of the tokens left, of everyone's scores,
        #and everyone's prior moves. However, the opponents will be put in a 
        #random order.
        f = open( "Results/games.log", "a")
        f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The players are " + str( self.algorithm_tuple ) + "\n" )
        f.close()
        while len(self.tokens) > 1:
            current_moves = []
            for i in range(len(self.algorithm_list)):
                others = copy.copy(self.algorithm_list)
                player_list = others.pop(i)
                random.shuffle( others )
                data = []
                data.append( player_list[1:] )
                for x in others:
                    data.append( x[1:] )#Does player_tuple[0] call the algorithm? ***
#                print self.tokens,data
                f = open( "Results/games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Calling Player " + str(i) + " which is " + str(player_list[0] )  + "\n" )
                f.close()
                this_move = player_list[0].choose_token( copy.deepcopy(self.tokens), copy.deepcopy(data), self.name )
                current_moves.append( this_move )
                f = open( "Results/games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Player " + str(i) + " responds " + str(this_move )  + "\n" )
                f.close()
            c = collections.Counter(current_moves)
            for i in range(len(self.algorithm_list)):
                player_list = self.algorithm_list[i]
                player_list[2].append(current_moves[i])
                if c[current_moves[i]] == 1:
                    player_list[1] += current_moves[i]
            new = []
            for x in self.tokens:
                if x not in current_moves:
                    new.append(x)
            self.tokens = new
            temp_scores = []
            for x in self.algorithm_list:
                temp_scores.append( x[1] )
            f = open( "Results/games.log", "a")
            f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The intermediate scores are " + str(temp_scores)  + "\n" )
            f.close()
        if len(self.tokens) == 1:
            item = self.tokens.pop(0)
            i = 0
            for player_list in self.algorithm_list:
                i += 1
                player_list[2].append( item )
                f = open( "Results/games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Player " + str(i) + " (having one move left) gets " + str(item)  + "\n" )
                f.close()
                if len(self.algorithm_list) == 1:#In the unusual 1-player case, the last token is won
                    player_list[1] += item
        temp_scores = []
        for x in self.algorithm_list:
                temp_scores.append( x[1] )
        f = open( "Results/games.log", "a")
        f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The intermediate scores are " + str(temp_scores)  + "\n" )
        f.close()
        max = 0
        for player_list in self.algorithm_list:
            score = player_list[1]
            if max < score:
                max = score
        self.results = []
        count = 0
        for player_list in self.algorithm_list:
            score = player_list[1]
            if max == score:
                count += 1
        for player_list in self.algorithm_list:
            score = player_list[1]
            if max == score:
                self.results.append( float( len(self.algorithm_list) ) / count )
            else:
                self.results.append( 0 )
        self.duration = time.time() - self.start_time
        to_write = "Official: Game:"
        for x in self.algorithm_tuple:
            to_write += " " + str(x)
        to_write += "\n\t"
        to_write += "Here is the score_tuple: " + str(self.results) + "\n\t"
        to_write += "This game's name is " + self.name + "\n\t"
        to_write += "This game took " + str( self.duration ) + " seconds.\n"
        self.to_write = to_write
        f = open( "Results/games.log", "a")
        f.write( time.asctime() + ": " + self.to_write )
        f.close()

