# cython: profile=False
#The first line might make it slower when profile = True.
import numpy as np
cimport numpy as np
#from libcpp cimport bool
from cpython cimport bool
import collections
import pickle
from libc.stdlib cimport rand, RAND_MAX
cdef int NUM_PLAYERS = 5
cdef list TOKENS = range(1,16)
class Neural_Nash_Untrainable_Wrapper:
    '''Makes a decision using aux_stochastic and a neural network trained through backpropagation.
    This class is optimized for decision speed. It has no do_training method.'''
    def __init__(self):
        self.model = self.get_standard_model()
        self.load()
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
        cdef np.ndarray[np.int_t,
                    ndim=1,
                    negative_indices=False,
                    mode='c'] array_tokens
        array_tokens = np.zeros( shape = ( len(tokens) ), dtype = long )
        i = 0
        for i in range(len(tokens)):
            array_tokens[i] = <int>tokens[i]
        return aux_stochastic(self, array_tokens, scores_so_far)
    def load(self):
        f = open("Results/neural_nash_current_model.p","rb")
        self.model.set_weights(pickle.load(f))
        f.close()
    def get_standard_model(self):
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
    cdef int i
    cdef np.ndarray[np.float_t, ndim=1, negative_indices=False, mode='c'] one_d_results = np.zeros( (NUM_PLAYERS,), dtype = np.float)
    if tokens == []:
        highest_score = max(current_scores)
        num_winners = list(current_scores).count(highest_score)
        i = 0
        for i in range(NUM_PLAYERS):
            if current_scores[i] == highest_score:
                one_d_results[i] = <float>NUM_PLAYERS / num_winners 
        return one_d_results
    scores = []
    for item in current_scores:
        scores.append( item )
    c = collections.Counter(tokens)
    existing_tokens = []
    for i in TOKENS:
        existing_tokens.append( c[i] )
    l = len( existing_tokens ) + len( scores )
    the_input = np.array( existing_tokens + scores)
    the_input.shape = (1,l)
#    print the_input
    results = player.model.predict( the_input )
#    print results
    i = 0
    for i in range(NUM_PLAYERS):
        one_d_results[i] = <float>(NUM_PLAYERS * results[0,i])
    return one_d_results
cdef aux_abridged_game(object player, np.ndarray[np.int_t, ndim=1, negative_indices=False, mode='c'] tokens,
                          np.ndarray[np.int_t, ndim=1, negative_indices=False, mode='c'] players_choices,
                         np.ndarray[np.double_t, ndim=1, negative_indices=False, mode='c'] scores_so_far):
    '''This version of game receives the position and the current moves.
    Then it plays one round and returns the utilities for Neural_Nash.
                The sum of utility assigned is n. 
                Utility is always positive. The rest 
                is up to the neural network, which ought to assign utilities that
                match expected utilities in the real game.
    '''
    cdef list new
    cdef np.ndarray[np.double_t, ndim=1, negative_indices=False, mode='c'] this_case_scores
    this_case_scores = np.copy(scores_so_far)
    c = collections.Counter(players_choices)
    cdef int i = 0
    for i in range(NUM_PLAYERS):
        if c[players_choices[i]] == 1:
            this_case_scores[i] = players_choices[i] + this_case_scores[i]
    new = []
    for x in tokens:
        if x not in players_choices:
            new.append(x)
    return aux_evaluate_position(player, new, this_case_scores)
cdef aux_stochastic(object player, np.ndarray[np.int_t, ndim=1, negative_indices=False, mode='c'] tokens,
                    np.ndarray[np.double_t, ndim=1, negative_indices=False, mode='c'] scores_so_far,
                    int start = 25, int memory = 50, int available = 25, int end = 200):
    cdef dict utility_record = {}
    cdef long [:] view_tokens = tokens
    cdef np.ndarray[np.int_t,
                ndim=2,
                negative_indices=False,
                mode='c'] actual_choices
    actual_choices = np.zeros( (end, NUM_PLAYERS), dtype = np.int)
    cdef long [:,:] view_actual_choices = actual_choices
    cdef int i,j,l,k, 
    cdef int max_index
    cdef double max_so_far, this_sum
    cdef int token_len = <int>np.size(tokens)
    i = 0
    for i in range(start):
        j = 0
        for j in range(NUM_PLAYERS):
            view_actual_choices[i,j] = view_tokens[ <int>(rand()/(RAND_MAX*1.0) * token_len)  ]
    #At this point view_actual_choices has been initialized with random moves
    cdef int count = start
    cdef np.ndarray[np.float_t,
                ndim=2,
                negative_indices=False,
                mode='c'] my_utilities = np.zeros( (1,1) , dtype = np.float)
    cdef double[:,:] view_my_utilities 
    cdef double[:] view_temp_utilities
    cdef np.ndarray[np.int_t,
                ndim=1,
                negative_indices=False,
                mode='c'] player_moves = np.zeros( (NUM_PLAYERS,) , dtype = np.int)
    cdef long [:] view_player_moves = player_moves
    cdef np.ndarray[np.int_t,
                ndim=1,
                negative_indices=False,
                mode='c'] imagined_player_moves = np.zeros( (NUM_PLAYERS,) , dtype = np.int)
    cdef long [:] view_imagined_player_moves = imagined_player_moves
    cdef int currently_remembered_index
    cdef int where_memory_starts
    cdef int possibly_abridged_memory
    cdef int ii
    my_utilities = np.zeros(   (   token_len , available ) , dtype = np.double)
    view_my_utilities = my_utilities
    cdef tuple lookup_tuple
    for count in range(start,end):#Now we are in the next decision-time
        where_memory_starts = max( count - memory, 0 )
        possibly_abridged_memory = count - where_memory_starts
        i = 0
        for i in range(token_len):
            ii = 0 
            for ii in range(available):
                view_my_utilities[i,ii] = 0
        i = 0
        for i in range(NUM_PLAYERS):
           #Now we've chosen a player
            j = 0
            for j in range(available):
                currently_remembered_index = <int>(rand()/(RAND_MAX*1.0) * possibly_abridged_memory) + where_memory_starts
                ii = 0 
                for ii in range(NUM_PLAYERS):
                    view_player_moves[ii] = view_actual_choices[count - currently_remembered_index,ii]
                #player_moves is everyone's actual moves at the index we remember
                l = 0
                for l in range(token_len):#Now we change the tokens I played to see if I could do better
                    ii = 0
                    for ii in range(NUM_PLAYERS):
                        view_imagined_player_moves[ii] = view_player_moves[ii]
                    view_imagined_player_moves[i] = view_tokens[l]
                    lookup_tuple = tuple(imagined_player_moves)
                    #Now play the game and update utilities
                    #Saving a dictionary speeds it up by a factor of 17, starting with tokens from 1 to 15
                    try:
                        view_temp_utilities = utility_record[lookup_tuple]
                    except KeyError:
                        view_temp_utilities = aux_abridged_game(player, tokens, imagined_player_moves, scores_so_far)
                        utility_record[lookup_tuple] = view_temp_utilities
#                    view_temp_utilities = aux_abridged_game(player, tokens, imagined_player_moves, scores_so_far)
                    view_my_utilities[l,j] = view_temp_utilities[i]
            l = 0
            max_so_far = 0 
            max_index = 0
            for l in range(token_len):
                this_sum = 0
                j = 0
                for j in range(available):
                    this_sum = this_sum + view_my_utilities[l,j]
                if this_sum > max_so_far:
                    max_so_far = this_sum
                    max_index = <int>l
            view_actual_choices[count,i] =  view_tokens[ max_index ] 
#            print actual_choices
    cdef int choice_index
    choice_index = 1 + <int>(rand()/(RAND_MAX*1.0) * memory)#Does this end at memory? Yes, it's inclusive.
#    print len(utility_record.keys())
    return view_actual_choices[end-choice_index,0]