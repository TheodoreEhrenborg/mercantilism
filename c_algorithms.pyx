import numpy as np
cpdef class Neural_Nash_Untrainable_Wrapper:
    cpdef __init__(self):
        self.player = Neural_Nash_Untrainable()
    cpdef actually_choose_token(self, list tokens, list data):
        return self.player.aux_stochastic(tokens, data)
cdef class Neural_Nash_Untrainable:
    '''Makes a decision using aux_stochastic and a neural network trained through backpropagation.
    This class is optimized for decision speed. It has no do_training method.'''
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
    cdef __init__(self):
        from tensorflow.keras.models import Sequential
        cdef Sequential self.model = self.get_standard_model()
        self.load()
    cdef load(self):
#        import pickle
        f = open("Results/neural_nash_current_model.p","rb")
        self.model.set_weights(pickle.load(f))
        f.close()
    cdef aux_evaluate_position( self, list tokens, list current_scores):
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
    cdef get_standard_model(self):
 #       import tensorflow.keras
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Activation, Dropout
        from tensorflow.keras.optimizers import SGD
        cdef Sequential model = Sequential()
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
    cdef aux_abridged_game(self, tokens, players_choices, scores_so_far):
#    import random, collections, copy
        '''This version of game receives the position and the current moves.
        Then it plays one round and returns the utilities for Neural_Nash.
                    The sum of utility assigned is n. 
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
        return self.aux_evaluate_position( tokens, scores_so_far)
    cdef aux_stochastic(self, list tokens, list data, int start = 25, int memory = 50, int available = 25, int end = 200):
        utility_record = {}
        cdef int n = len(data) #n is the number of players
        cdef tuple tokens = tuple(tokens)
        scores_so_far_l = []
        for item in data:
            scores_so_far_l.append( item[0]  )
        cdef tuple scores_so_far = tuple(scores_so_far_l)
        actual_choices = np.zeros( (n, end), dtype = numpy.int8)
        cdef int i = 0
        for i in range(n):
            temp = []
            cdef int j = 0
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
                        my_utilities[l].append( temp_utilities[i] )
                summed = []
                for x in my_utilities:
                    summed.append(  self.list_total(x) )
                best_move = tokens[ summed.index( max(summed) ) ]
                actual_choices[i].append( best_move )
        return random.choice( actual_choices[0][-memory:] )
