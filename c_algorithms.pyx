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
    if isinstance(utility_metric, Neural_Nash) and utility_metric.is_training:
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
