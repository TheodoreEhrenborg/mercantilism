'''This file contains the various algorithms that play the game.
Methods starting with aux_ are not playing the game.'''
import numpy as np
import random, collections, time, copy, pickle, os
TOKENS = range(1,16)
NUM_PLAYERS = 5
def play_highest(tokens, data, game_name):
    '''Plays the highest token left.'''
#    import time
    f = open("Results/play_highest.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) + ". \n")
    choice = max( tokens )
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def uniform(tokens, data, game_name):
    '''Plays a token randomly, chosen based on a uniform distribution.'''
#    import time, random
    f = open("Results/uniform.log","a")
    f.write(time.asctime() + ": Got message from Game " + game_name + ". Tokens received " + str(tokens) + ". Data received " + str(data) + ". \n")
    choice = random.choice( tokens )
    f.write(time.asctime() + ": Chose " + str(choice) + "\n")
    f.close()
    return choice
def aux_exp(tokens, data, game_name, n):
    '''Plays a token based on a distribution where each token is chosen with 
    weight proportional to n^(value) '''
#    import time, random
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
#    import time, random
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
#    import random, time
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
#        import copy
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
#        import random
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
#        import random
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
#def neural_evolve():
#    pass
#def neural_evolve(tokens, data, game_name):
#    return NEURAL_EVOLVER_INSTANCE.choose_token( tokens, data, game_name )
class Neural_Evolver:
    '''Makes a decision using a neural network trained through artificial selection'''
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
    def evolve(cls, generations = 5 , trials_per_generation = 100, mutation_size = 0.1, mutation_chance = 0.2, population = 15, chance_a_player_mutates = 0.5):
#        import copy,time
        players = []
        for i in range(population):
            p = Neural_Evolver(i)
            players.append(p)
        indices = range( population )
        gen = 0
        while gen < generations:
            gen += 1
            t = time.time()
            #Now we update the players
            scores = []
            for i in range( population ):
                p = players[i]
                p.load()
                if random.random < chance_a_player_mutates:
                    p.mutate(chance = mutation_chance, how_far = mutation_size)
                scores.append(0)
            #Now play games and choose the best players
            for trial in range(trials_per_generation):
#                g = Game( copy.copy(players), copy.copy(TOKENS) )
                #Which players are playing during this trial?
                random.shuffle( indices )
                playing_indices = indices[0:NUM_PLAYERS]
                non_playing_indices = indices[NUM_PLAYERS:]
                playing_players = []
                for i in playing_indices:
                    playing_players.append( players[i] )
                g = Game( playing_players, copy.copy(TOKENS) )
                playing_players_scores = list(g.get_results())
                all_scores = copy.copy(playing_players_scores)
                for x in non_playing_indices:
                    all_scores.append( 1 )
                for current_index in range(len(indices)):
                    actual_index = indices[current_index]
                    this_players_score = all_scores[current_index]
                    scores[actual_index] += this_players_scores
                    #Non-players get 1 utility point, players get their scores
                #scores = cls.list_add( g.get_results(), scores)
            #Here's how we choose the best players:
            #Using the scores as weights, we choose as many indices as there are players in the population.
            #Indices can be chosen twice.
            #Then for every index that has been chosen, we go to that player and get it to save its data.
            #The first player to save does so in place 0, then place 1, ..., then place population-1
            #Remember that mutation is done at the beginning of the generation.
            accountant = players[0]
            #I need one player to use their method.
            for i in range(population):
                next_gen_index = accountant.get_token_from_weights( scores ) - 1
                next_gen_player = players[next_gen_index]
                next_gen_player.become_parent(which_label = i)
#            max_score = max(scores)
#            i = scores.index(max_score)
#            best = players[i]
#            #Some of them mutate before being saved
#            best.become_parent()
#            print max_score / (trials_per_generation), time.time() - t
#            clear_session()
#            for p in players:
#                p.delete()
#            print best
#        return best.model.get_weights()[0][0]
#        return max_score / (trials_per_generation)
    def __init__(self, return_to_default = False, i = 0):
#        try:
##            import tensorflow.keras
#            from tensorflow.keras.models import load_model
#            self.model = load_model('Results/current_model.h5')
        self. i = i
        try:
            self.model = self.get_standard_model()
            self.load()
        except IOError:#Is this the right error?
            self.model = self.get_standard_model()
            self.become_parent()
        if return_to_default:
            self.model = self.get_standard_model()
    def load(self):
#        import pickle
        f = open("Results/neural_evolver_current_model" + str(self.i) + ".p","rb")
        self.model.set_weights(pickle.load(f))
    def choose_token( self, tokens, data, game_name):
#        import collections,random
#        import numpy as np
        scores = []
        for item in data:
            scores.append( float(item[0]) / aux_list_total(TOKENS) )
        if tokens == []:
            print "tokens == []"
        c = collections.Counter(tokens)
        existing_tokens = []
        for i in TOKENS:
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
        if aux_list_total(zeroed_weights) == 0:
#            print weights, zeroed_weights
            choice = random.choice( tokens )
        else:
            choice = self.get_token_from_weights(zeroed_weights)
        return choice
    def get_token_from_weights(self, weights):
#        import random
#        weights.shape = (1,)
        sum = aux_list_total(weights)
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
        model.compile(optimizer='sgd',
          loss='categorical_crossentropy',
          metrics=['accuracy'])#These terms don't have any significance
        return model
    def become_parent(self, which_label = None):
#        import os,pickle
        i = self.i
        if which_label != None:
            i = which_label
        os.system("rm -f Results/neural_evolver_current_model" + str(i) + ".p")
        f = open("Results/neural_evolver_current_model" + str(i) + ".p","wb")
        pickle.dump( self.model.get_weights(), f)
        f.close()
    def mutate(self, chance = 0.2, how_far = 0.1):
#        import random,numpy
        how_far = abs(how_far)
        weights = self.model.get_weights()
        for i in range(len(weights)):
            ww = weights[i]
            for j in range(len(ww)):
                if type(ww[j]) == np.float32:
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
def neural_nash():
    pass
class Neural_Nash:
    '''Makes a decision using aux_stochastic and a neural setwork trained through backpropagation'''
    def do_training(self, generations = 5, games = 1000, max_complexity = None, training_epochs = 10, max_gen_time = 10**9):
        '''max_gen_time is the maximum time allowed to any generation (plus the time it takes to finish a game)'''
        count = 0
        players = []
        if max_complexity == None:
            max_complexity = len(TOKENS)
        self.max_complexity = max_complexity
        for x in range(NUM_PLAYERS):
            players.append( self )
        while count < generations:
            start_time = time.time()
            os.system("rm -f Results/neural_nash_data.p")
            count += 1
            #Play a lot of games
            game_count = 0
            while game_count < games and time.time() - start_time < max_gen_time:
                game_count += 1
                g = Game( players, copy.copy(TOKENS) )
            #Get the improved predictions from those games
            f = open("Results/neural_nash_data.p","rb")
            data = pickle.load(f)
            f.close()
            #data is a list of tuples, which are ( tokens ,scores, expected_utilities)
            the_input = []
            shadow_output = []
            for item in data:
                temp = []
                shadow_temp = []
                c = collections.Counter(item[0])
                for t in TOKENS:
                    temp.append(c[t])
                for s in item[1]:
#                    temp.append( float(s)/aux_list_total(TOKENS))
                    temp.append( s )
                    shadow_temp.append(s)
                shadow_output.append(shadow_temp)
                the_input.append(temp)
            the_input = np.array(the_input)
            shadow_output = np.array( shadow_output )
            #Scale the predictions to have a sum of 1
            the_output = []
            for item in data:
                temp = []
                for x in item[2]:
                    temp.append( float(x) / NUM_PLAYERS )
                the_output.append(temp)
            the_output = np.array(the_output)
#            the_output = shadow_output
            #Let the neural network train
#            self.randomize()
##            print the_input,the_output
            self.model.fit(the_input, the_output, epochs = training_epochs, batch_size=32)
            #Become the parent
            self.become_parent()
            os.system("cp Results/neural_nash_data.p Results/Old_Logs/neural_nash_data_" + time.asctime().replace(" ","_") + ".p")
#            time.sleep(1)
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
    def randomize(self):
#        import random,numpy
        weights = self.model.get_weights()
        for i in range(len(weights)):
            ww = weights[i]
            for j in range(len(ww)):
                if type(ww[j]) == np.float32:
                    weights[i][j] = random.random()
                else:
                    www = ww[j]
                    for k in range(len(www)):
                        weights[i][j][k] = random.random()
        self.model.set_weights( weights )
    def __init__(self, return_to_default = False):
        try:
            self.model = self.get_standard_model()
            self.load()
        except IOError:#Is this the right error?
            self.model = self.get_standard_model()
            self.become_parent()
        if return_to_default:
            self.model = self.get_standard_model()
    def load(self):
#        import pickle
        f = open("Results/neural_nash_current_model.p","rb")
        self.model.set_weights(pickle.load(f))
    def evaluate_position( self, tokens, data, game_name):
        scores = []
        for item in data:
            scores.append( item[0] )
        return self.aux_evaluate_position( tokens, scores)
    def aux_evaluate_position( self, tokens, current_scores):
#        import collections,random
#        import numpy as np
        if tokens == []:
            output = []
            highest_score = max(current_scores)
            num_winners = current_scores.count(highest_score)
            for i in range(NUM_PLAYERS):
                if current_scores[i] == highest_score:
                    output.append( float(NUM_PLAYERS) / num_winners )
                else:
                    output.append(0)
            return output
        scores = []
        for item in current_scores:
            scores.append( item )
#            scores.append( float(item) / aux_list_total(TOKENS) )
        c = collections.Counter(tokens)
        existing_tokens = []
        for i in TOKENS:
            existing_tokens.append( c[i] )
        l = len( existing_tokens ) + len( scores )
        the_input = np.array( existing_tokens + scores)
        the_input.shape = (1,l)
        #print the_input
        results = self.model.predict( the_input )
        #print results
        results_as_list = list(results[0])
        output = []
        for x in results_as_list:
            output.append( NUM_PLAYERS * x)
        return output
    def choose_token(self, tokens, data, game_name):
        if self.max_complexity >= len(tokens):
            aux_stochastic(tokens, data, game_name, self)
        return random.choice(tokens)
    def actually_choose_token(self, tokens, data, game_name):
        return aux_stochastic(tokens, data, game_name, self)
    def get_standard_model(self): 
 #       import tensorflow.keras
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Activation, Dropout
        from tensorflow.keras.optimizers import SGD
        model = Sequential()
        model.add(Dense(30, activation='relu', input_dim=20) )
        model.add(Dropout(0.5))
        model.add(Dense(30, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(5, activation='softmax'))
        model.compile(optimizer='sgd',
          loss='categorical_crossentropy',
          metrics=['accuracy'])
        return model
    def become_parent(self):
#        import os,pickle
        os.system("rm -f Results/neural_nash_current_model.p")
        f = open("Results/neural_nash_current_model.p","wb")
        pickle.dump( self.model.get_weights(), f)
        f.close()
#    def __str__(self):
#        return "Neural_Evolver: Weights are " + str(self.model.get_weights())
    def __str__(self):
        return "Neural_Nash"
    def __repr__(self):
        return "Neural_Nash"
class Game:
    '''This version of game assumes that the algorithms are objects, not functions'''
    def get_results(self):
        return tuple( self.results )
    def __init__(self, algorithm_tuple, tokens):
#        import random, collections, copy, time
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
        f = open( "Results/practice_games.log", "a")
        f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The players are " + str( self.algorithm_tuple ) + "\n" )
        f.close()
        while len(self.tokens) > 0:
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
                f = open( "Results/practice_games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Calling Player " + str(i) + " which is " + str(player_list[0] )  + "\n" )
                f.close()
                this_move = player_list[0].choose_token( copy.deepcopy(self.tokens), copy.deepcopy(data), self.name )
                current_moves.append( this_move )
                f = open( "Results/practice_games.log", "a")
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
            f = open( "Results/practice_games.log", "a")
            f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The intermediate scores are " + str(temp_scores)  + "\n" )
            f.close()
#        if len(self.tokens) == 1:
#            item = self.tokens.pop(0)
#            i = 0
#            for player_list in self.algorithm_list:
#                i += 1
#                player_list[2].append( item )
#                f = open( "Results/games.log", "a")
#                f.write( time.asctime() + ": Game " + self.name + ". Player " + str(i) + " (having one move left) gets " + str(item)  + "\n" )
#                f.close()
#                if len(self.algorithm_list) == 1:#In the unusual 1-player case, the last token is won
#                    player_list[1] += item
        temp_scores = []
        for x in self.algorithm_list:
                temp_scores.append( x[1] )
        f = open( "Results/practice_games.log", "a")
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
        f = open( "Results/practice_games.log", "a")
        f.write( time.asctime() + ": " + self.to_write )
        f.close()
        #data is a list of tuples, which are ( tokens ,scores, expected_utilities)
        data = [ self.tokens, temp_scores, self.results ]
        try:
            f = open("Results/neural_nash_data.p","rb")
        except IOError:
            to_pickle = []
            to_pickle.append(data)            
        else:
            to_pickle = pickle.load(f)
            to_pickle.append(data)
            f.close()
        f = open("Results/neural_nash_data.p","wb")
        pickle.dump( to_pickle, f )
        f.close()
def aux_abridged_game(tokens, players_choices, scores_so_far, utility_metric):
#    import random, collections, copy
    '''This version of game receives the position and the current moves.
    Then it plays one round and returns the utilities based on a 
    user-chosen function.
    Calculates a list containing the utility points of
    each player. Here are the options for utility_metric:
    'round_points': Utility is the number of points won this round
    'total_points': Utility is the number of points won in all rounds so far
    'round_diff': Utility is the difference between the points won in this round 
                  and the points won by the player (not this one) with the highest points
                  won this round
    'total_diff': Utility is the difference between the cumulative score so far and the
                  cumulative score of the player (not this one) with the highest 
                  cumulative score
    'round_winner': Utility is n (the number of players)
                    if this player received the highest number of points
                    this round. Utility is 0 otherwise. (Technically, if there is a 2-tie the
                    two winners each receive n/2 points, etc.)
    'total_winner': Utility is assigned just like in the previous option, but winners are
                    determined based on the total amount of points won.
    When utility_metric is a Neural_Nash instance: The sum of utility assigned is n. 
                    Utility is always positive. The rest 
                    is up to the neural network, which ought to assign utilities that
                    match expected utilities in the real game.
    '''
    n = len(players_choices)
    c = collections.Counter(players_choices)
    round_scores = []
    scores_so_far = list(scores_so_far)
    tokens = list(tokens)
    for i in range(n):
        if c[players_choices[i]] == 1:
            round_scores.append( players_choices[i] )
            scores_so_far[i] += players_choices[i]
        else:
            round_scores.append(0)
        new = []
        for x in tokens:
            if x not in players_choices:
                new.append(x)
        tokens = new
    if utility_metric == 'round_points':
        return round_scores
    elif utility_metric == 'total_points':
        return scores_so_far
    elif utility_metric == 'round_diff':
        output = []
        for i in range(n):
            other_scores = round_scores[:i] + round_scores[i+1:]
            output.append( round_scores[i] - max(other_scores) )
        return output
    elif utility_metric == 'total_diff':
        output = []
        for i in range(n):
            other_scores = scores_so_far[:i] + scores_so_far[i+1:]
            output.append( scores_so_far[i] - max(other_scores) )
        return output
    elif utility_metric == 'round_winner':
        output = []
        highest_score = max(round_scores)
        num_winners = round_scores.count(highest_score)
        for i in range(n):
            if round_scores[i] == highest_score:
                output.append( float(n) / num_winners )
            else:
                output.append(0)
        return output
    elif utility_metric == 'total_winner':
        output = []
        highest_score = max(scores_so_far)
        num_winners = scores_so_far.count(highest_score)
        for i in range(n):
            if scores_so_far[i] == highest_score:
                output.append( float(n) / num_winners )
            else:
                output.append(0)
        return output
    elif isinstance( utility_metric, Neural_Nash):
        return utility_metric.aux_evaluate_position( tokens, scores_so_far)
    else:
        raise Exception("Could not recognize option " + utility_metric)
def aux_list_total(a):
    total = 0
    for x in a:
        total += x
    return total
def round_points(tokens, data, game_name):
    return aux_stochastic(tokens, data, game_name, 'round_points')
def total_points(tokens, data, game_name):
    return aux_stochastic(tokens, data, game_name, 'total_points')
def round_diff(tokens, data, game_name):
    return aux_stochastic(tokens, data, game_name, 'round_diff')
def total_diff(tokens, data, game_name):
    return aux_stochastic(tokens, data, game_name, 'total_diff')
def round_winner(tokens, data, game_name):
    return aux_stochastic(tokens, data, game_name, 'round_winner')
def total_winner(tokens, data, game_name):
    return aux_stochastic(tokens, data, game_name, 'total_winner')
def aux_stochastic(tokens, data, game_name, utility_metric, start = 25, memory = 50, available = 25, end = 200):
#    import random
    utility_record = {}
    n = len(data)
    tokens = tuple(tokens)
    scores_so_far = []
    for item in data:
        scores_so_far.append( item[0]  )
    scores_so_far = tuple(scores_so_far)
    actual_choices = []
    for i in range(n):
        temp = []
        for j in range(start):
            temp.append( random.choice(tokens) )
        actual_choices.append( temp )
    #At this point actual_choices has been initialized with random moves
    count = start
    while count <= end:
        count += 1
        for i in range(n):
            #Now we've chosen a player
            temp = range(   min(   memory, len(actual_choices[i])  )   )
            random.shuffle( temp )
            remembered_indices = temp[0:available]
            my_utilities = []
            for l in tokens:
                my_utilities.append( [] )
            for j in remembered_indices:
                player_moves = []
                for k in range(n):
                    player_moves.append( actual_choices[k][j] )
                for l in range(len(tokens)):
                    imagined_player_moves = player_moves[:]
                    imagined_player_moves[i] = tokens[l]
                    imagined_player_moves = tuple(imagined_player_moves)
                    #Now play the game and update utilities
                    #Saving a dictionary speeds it up by a factor of 17, starting with tokens from 1 to 15
                    try: 
                        temp_utilities = utility_record[(tokens, imagined_player_moves, scores_so_far)]
                    except KeyError:
                        temp_utilities = aux_abridged_game(tokens, imagined_player_moves, scores_so_far, utility_metric)
                        utility_record[(tokens, imagined_player_moves, scores_so_far)] = temp_utilities
#                    temp_utilities = aux_abridged_game(tokens, imagined_player_moves, scores_so_far, utility_metric)
                    my_utilities[l].append( temp_utilities[i] )
            summed = []
            for x in my_utilities:
                summed.append(  aux_list_total(x) )
            best_move = tokens[ summed.index( max(summed) ) ]
            actual_choices[i].append( best_move )
    if isinstance(utility_metric, Neural_Nash):
        results = []
        for x in range(n):
            results.append(0)
        for x in range(1,memory):
            temp  = []
            for y in range(n):
                temp.append( actual_choices[y][-x] )
            try:
                expected = utility_record[(tokens, tuple(temp), scores_so_far)]
            except KeyError:
                expected = aux_abridged_game(tokens, tuple(temp), scores_so_far, utility_metric)
                utility_record[(tokens, tuple(temp), scores_so_far)] = temp_utilities
            results = Neural_Nash.list_add( expected, results)
        new_results = []
        for item in results:
            new_results.append( float(item)/memory )
        data = ( tokens ,scores_so_far,new_results)
        #Now I need to pickle these results along with the 
        #tokens and scores_so_far. But I shouldn't
        #overwrite the data that is already there.
        try:
            f = open("Results/neural_nash_data.p","rb")
        except IOError:
            to_pickle = []
            to_pickle.append(data)            
        else:
            to_pickle = pickle.load(f)
            to_pickle.append(data)
            f.close()
        f = open("Results/neural_nash_data.p","wb")
        pickle.dump( to_pickle, f )
        f.close()
#    print actual_choices
    return random.choice( actual_choices[0][-memory:] )
