import numpy as np
cimport numpy as np
import collections, random
import pickle
cdef long NUM_PLAYERS = 5
cdef list TOKENS = range(1,16)
class Neural_Nash_Untrainable_Wrapper:
    def __init__(self):
        self.player = Neural_Nash_Untrainable()
    def actually_choose_token(self,  tokens,  data):
        cdef list scores_so_far_l = []
        for item in data:
            scores_so_far_l.append( item[0]  )
        cdef np.ndarray[np.float_t,
                    ndim=1,
                    negative_indices=False,
                    mode='c'] scores_so_far
        scores_so_far = np.zeros( shape = ( len(scores_so_far_l) ) )
        cdef int i = 0
        for i in range(len(scores_so_far_l)):
            scores_so_far[i] = scores_so_far_l[i]
        cdef np.ndarray[np.long_t,
                    ndim=1,
                    negative_indices=False,
                    mode='c'] array_tokens
        array_tokens = np.zeros( shape = ( len(tokens) ), dtype = long )
#        array_tokens = [1,2]
#        array_tokens = np.array(tokens)
        i = 0
        for i in range(len(tokens)):
            array_tokens[i] = tokens[i]
        return aux_stochastic(self.player, array_tokens, scores_so_far)
class Neural_Nash_Untrainable:
    '''Makes a decision using aux_stochastic and a neural network trained through backpropagation.
    This class is optimized for decision speed. It has no do_training method.'''
    def __init__(self):
#        from tensorflow.keras.models import Sequential
        self.model = self.get_standard_model()
        self.load()
    def load(self):
#        import pickle
        f = open("Results/neural_nash_current_model.p","rb")
        self.model.set_weights(pickle.load(f))
        f.close()
    def get_standard_model(self):
#        import tensorflow.keras
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
    def __str__(self):
        return "Neural_Nash"
    def __repr__(self):
        return "Neural_Nash"
cdef aux_evaluate_position( object player, list tokens, 
     np.ndarray[np.double_t, ndim=1, negative_indices=False, mode='c'] current_scores):
#    import collections,random
#    import numpy as np
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
#        scores.append( float(item) / sum(TOKENS) )
    c = collections.Counter(tokens)
    existing_tokens = []
    for i in TOKENS:
        existing_tokens.append( c[i] )
    l = len( existing_tokens ) + len( scores )
    the_input = np.array( existing_tokens + scores)
    the_input.shape = (1,l)
    #print the_input
    results = player.model.predict( the_input )
    #print results
    results_as_list = list(results[0])
    output = []
    for x in results_as_list:
       output.append( NUM_PLAYERS * x)
    return output
cdef aux_abridged_game(object player, np.ndarray[np.long_t, ndim=1, negative_indices=False, mode='c'] tokens,
                         list players_choices,
                    	 np.ndarray[np.double_t, ndim=1, negative_indices=False, mode='c'] scores_so_far):
#    import random, collections, copy
    '''This version of game receives the position and the current moves.
    Then it plays one round and returns the utilities for Neural_Nash.
                The sum of utility assigned is n. 
                Utility is always positive. The rest 
                is up to the neural network, which ought to assign utilities that
                match expected utilities in the real game.
    '''
    cdef list new
    cdef long n = len(players_choices)
    c = collections.Counter(players_choices)
#    round_scores = []
#    scores_so_far = list(scores_so_far)
#    tokens = list(tokens)
    cdef long i = 0
    for i in range(n):
        if c[players_choices[i]] == 1:
#           round_scores.append( players_choices[i] )
            scores_so_far[i] = players_choices[i] + scores_so_far[i]
#        else:
#            round_scores.append(0)
    new = []
    for x in tokens:
        if x not in players_choices:
            new.append(x)
    return aux_evaluate_position(player, new, scores_so_far)
cdef aux_stochastic(object player, np.ndarray[np.long_t, ndim=1, negative_indices=False, mode='c'] tokens,
                    np.ndarray[np.double_t, ndim=1, negative_indices=False, mode='c'] scores_so_far,
                    long start = 25, long memory = 50, long available = 25, long end = 200):
    utility_record = {}
    cdef long n = len(scores_so_far) #n is the number of players
    cdef np.ndarray[np.long_t,
                ndim=2,
                negative_indices=False,
                mode='c'] actual_choices
    actual_choices = np.zeros( (end, n), dtype = np.long)
    cdef long i,j,l,k
    i = 0
    for i in range(start):
        j = 0
        for j in range(n):
            actual_choices[i,j] = random.choice(tokens)
    #At this point actual_choices has been initialized with random moves
    count = start
    while count < end - 1:
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
                k = 0
                for k in range(n):
                    player_moves.append( actual_choices[j,k] )
                l = 0
                for l in range(len(tokens)):
                    imagined_player_moves = player_moves[:]
                    imagined_player_moves[i] = tokens[l]
                    imagined_player_moves = list(imagined_player_moves)
                    #Now play the game and update utilities
                    #Saving a dictionary speeds it up by a factor of 17, starting with tokens from 1 to 15
                    try: 
                        temp_utilities = utility_record[(str(tokens), tuple(imagined_player_moves), str(scores_so_far))]
                    except KeyError:
                        temp_utilities = aux_abridged_game(player, tokens, imagined_player_moves, scores_so_far)
                        utility_record[(str(tokens), tuple(imagined_player_moves), str(scores_so_far))] = temp_utilities
                    my_utilities[l].append( temp_utilities[i] )
            summed = []
            for x in my_utilities:
                summed.append(  sum(x) )
            best_move = tokens[ summed.index( max(summed) ) ]
            actual_choices[count,i] =  best_move 
    return random.choice( actual_choices[end-memory:][0] )
