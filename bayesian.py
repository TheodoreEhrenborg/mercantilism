import cdecimal, random, time, math
import pyximport
pyximport.install()
import c_bayesian
Decimal = cdecimal.Decimal
import numpy as np
import os
DEFAULT = 0.0
NUM_PLAYERS = 5
TOKENS = range(1, 15+1)
def main(game_results = range(32), trials = 1e4, test_case = None, final_diff_exp = -10):
    '''Uses five dimensions with multiplicities and the Decimal class'''
    #Note that game_results is of the form ( x , y , ... , w )
    #where each value is the number of times a game has had a certain outcome (like the first and third players tie)
    #However, the first element of game_results is zero because all players cannot all lose
    #import Monte Carlo integration algorithm from scikit-monaco library
#    f = open("Results/bayesian.log","a")
#    f.write(time.asctime() + ": Got game_results = " + str(game_results) + 
#            " Got trials = " + str(trials) + "\n")
#   f.close()
    #n is the number of players
    n = int( math.log( len(game_results) , 2) )
    compressed = []
    multiplicities = []
    weights = []
    for x in range(n+1):
        compressed.append(0)
        multiplicities.append(0)
        weights.append(0)
    for i in range( 1, len(game_results) ):
        base_2 = to_base_2(i)
        c = sum(base_2)
        if base_2[-1] == 0:
            compressed[0] += game_results[i]
            multiplicities[0] += 1
            weights[0] = 0 #Note that losses come first, then wins, 2-ties, ..., n-ties
        else:
            compressed[c] += game_results[i]
            multiplicities[c] += 1
            weights[c] =  float(n)/c
    if test_case != None:
        compressed = test_case
#    print compressed, weights, multiplicities
    #Now I need to run below_average_cases. I should figure out the 
    #weights of each outcome -- a win is n points -- and the average 
    #utility points to beat. I'll do that here instead of in the 
    #thousands of runs of below_average_cases.
    average = 1
    abridged = game_results[1:]
    #integrate all probabilities over the hypercube
    #For n players, a game could end in 2^n - 1 ways
    best_point_tuple = tuple( normalize( compressed ) )
    old_lowers = None
    old_uppers = None
    results = np.array([ Decimal(0), Decimal(0) ])
    for e in range(final_diff_exp,1):
        diff = 2**e
        sample_lowers = np.zeros( (n,) )
        sample_uppers = np.ones( (n,) )
        for i in range(n):
            x = best_point_tuple[i]
            sample_lowers[i] = max( x - diff, 0)
            sample_uppers[i] = min(x + diff, 1) 
        results += integrate( both , args = [compressed, weights, average, multiplicities],
                            npoints = long(trials), lowers = sample_lowers, uppers = sample_uppers,
                            excluded_lowers = old_lowers, excluded_uppers = old_uppers)
        old_lowers = sample_lowers
        old_uppers = sample_uppers
    total = results[0]
    below = results[1]
#    f = open("Results/bayesian.log","a")
#    f.write(time.asctime() + ": Calculated total probability = " + str(total) + "\n")
#    f.write(time.asctime() + ": Calculated below average probability = " + str(below) + "\n")
#    f.close()
    #Divide to get the chance that 1 is not ES against 2
    #No, it's the chance that the fixed strategy is ES against the invader
    return  below / total
def both( point, args ):
    compressed_game_results = args[0]
    weights = args[1]
    average = args[2]
    multiplicities = args[3]
#    point = list( point_tuple )
    point.sort()
#    point = [0] + point + [1,]
    density = Decimal(1)
#    average_multiplier = 0
    for i in range( len(compressed_game_results) ):
        how_many_games = compressed_game_results[i]
        m = multiplicities[i]
        interval = Decimal( point[i+1] - point[i] )
#        print interval, how_many_games
#        average_multiplier += interval * m
        density *= interval ** how_many_games
        density *= interval ** (m-1)
#        except decimal.InvalidOperation:
#            print point, interval
#        density *= m ** interval
#    density *= average_multiplier
    result1 = density
    expected_utility = 0
    for i in range( len(weights) ):
        expected_utility += weights[i] *  ( point[i+1] - point[i] )
    if expected_utility < average:
        result2 = result1
    elif expected_utility > average:
        result2 = 0
    else:
        result2 = 0.5 * result1
#    print result1, result2, density
    return np.array( [result1,result2] ) 
def list_total( l ):
    t = 0
    for x in l:
        t += x
    return t
def normalize( l ):
    t = list_total( l )
    new = []
    this_value = 0
    for x in l[:-1]:
        this_value = float(x) / t + this_value
        new.append( this_value )
#    print new, l
    return new
def to_base_2(x):
    '''x is a positive integer. Returns a list that is x in base 2.
    For instance, 22 becomes [1, 0, 1, 1, 0] and 0 becomes []''' 
    x = int( x )
    result = []
    while x > 0:
        if x % 2:
            result.append(1)
        else:
            result.append(0)
        x = x/2
    result.reverse()
    return result
def integrate( function, args, npoints, lowers, uppers, excluded_lowers = None, excluded_uppers = None):
    '''Finds the integral of the function in the box from lowers to uppers, not including
    the box from excluded_lowers to excluded_uppers'''
    dim = len(lowers)
    if dim != len(uppers):
        raise Exception("Dimension error")
    #If the following is True, don't worry about excluded areas
    go_for_it = not isinstance(excluded_lowers, np.ndarray)
    total = np.array( [Decimal(0),Decimal(0)] )
    this_point = np.zeros(dim + 2)
    this_point[dim + 2 - 1] = 1
    for i in range(npoints):
        for j in range(dim):
            r = random.random()
            rand_value = lowers[j] + r * ( uppers[j] - lowers[j] )
            this_point[j+1] = rand_value
#        if not go_for_it:
#            print np.any(this_point - excluded_lowers) < 0
        if go_for_it or np.min(this_point[1:-1] - excluded_lowers) < 0 or np.min(excluded_uppers - this_point[1:-1]) < 0: 
            density = function( this_point, args )
#            print density
            total += density
#    print total, total/ float(npoints)
    volume = np.abs( np.product( uppers - lowers ) )
    return Decimal(volume) * total / Decimal(npoints)
def run(file_name = None, trials = 1e4):
    import pickle
    if file_name == None:
        comparisons = use_log()
        for x in comparisons.keys():
#            if str(x[0]) == "total_winner" and str(x[1]) == "quick_evolve":
            comparisons[x] = check_probability(x, trials = trials)
        name = "Results/comparisons " + time.asctime() + ".p"
        name = name.replace(" ","_")
        f = open(name,"wb")
        pickle.dump( comparisons, f )
        f.close()
    else:
        f = open(file_name, "rb")
        comparisons = pickle.load(f)
        f.close()
    get_results(comparisons)
def use_log():
    import time, inspect, algorithms, pickle
    comparisons = {}
    temp = inspect.getmembers( algorithms, inspect.isfunction)
#    print temp
#    print list_algorithms
#    should_quit = True
    #***Make sure we can only get algorithms without aux_ in __name__
    list_algorithms = []
    for x in temp:
        wrapped = Wrapper(x)
        if wrapped.get_name()[0:4] != "aux_":
            list_algorithms.append( wrapped )
    f = open("Results/api.log","r")
    lines = f.readlines()
    f.close()
    lines.reverse()
    for line in lines:
        if "Official: Confidence: " in line:
            confidence = float( line.partition("Official: Confidence: ")[2] )
            break
    for line in lines:
        if "Official: Min_time: " in line:
            min_time = int( line.partition("Official: Min_time: ")[2] )
            break
    for line in lines:
        if "Official: Max_time: " in line:
            max_time = int( line.partition("Official: Max_time: ")[2] )
            break
    for line in lines:
        if "Official: Min_trials: " in line:
            min_trials = int( line.partition("Official: Min_trials: ")[2] )
            break
    for line in lines:
        if "Official: Max_trials: " in line:
            max_trials = int( line.partition("Official: Max_trials: ")[2] )
            break
    for i in range(len(list_algorithms)):
        for j in range(len(list_algorithms)):
            a = list_algorithms[i]
            b = list_algorithms[j]
            if a != b:
                current_confidence = DEFAULT
                key = "Official: Current Confidence: " + str(a) + " " + str(b) + " "
                found = False
                for line in lines:
                    if "Official: Reset " + str(a) + " " + str(b) in line:
                        break
                    if "Official: Reset " + str(a) + " " + "all" in line:
                        break
                    if "Official: Reset " + "all" + " " + str(b) in line:
                        break
                    if "Official: Reset " + "all" + " " + "all" in line:
                        break
                    if "Official: Redo_confidence" in line:
                        break
                    if key in line:
                        current_confidence = float( line.partition(key)[2] )
                        found = True
                        break
                comparisons[ (a,b) ] = (current_confidence, 0, 0, None, None, 0)
                #(confidence, num_trials, total_time,sum_trials, all_game_results, bayesian trials used)
    return comparisons
def check_probability(algorithm_tuple, trials = 1e4):
    import time
    f = open("Results/api.log","r")
    lines = f.readlines()
    f.close()
    lines.reverse()
    a, b = algorithm_tuple
    current_confidence = DEFAULT
    to_write_confidence = "Official: Current Confidence: " + str(a) + " " + str(b) + " "
    to_write_trials = "Official: Total Trials: " + str(a) + " " + str(b) + " "
    to_write_time = "Official: Total Time: " + str(a) + " " + str(b) + " "
    to_write_sum = "Official: Total Score: " + str(a) + " " + str(b) + " "
#    master_key = "Official: Game where " + str(a) + " is invaded by " + str(b) + "."
    master_key = "Official: Game:"
    for i in range(NUM_PLAYERS - 1):
        master_key += " " + str(a)
    master_key += " " + str(b)
    time_key = "This game took "
    results_key = "Here is the score_tuple: "
    all_game_results = []
    sum_game_results = []
    for i in range(NUM_PLAYERS):
        sum_game_results.append( 0 )
    for i in range(2**NUM_PLAYERS ):
        all_game_results.append( 0 )
    all_game_trials = 0
    all_game_time = 0
#     this_game_time = 0
    for line in lines:
        if "Official: Reset " + str(a) + " " + str(b) in line:
            break
        if "Official: Reset " + str(a) + " " + "all" in line:
            break
        if "Official: Reset " + "all" + " " + str(b) in line:
            break
        if "Official: Reset " + "all" + " " + "all" in line:
            break
        if time_key in line:
            new_line = line.partition(time_key)[2]
            new_line = new_line.strip("\n seconds.")
            this_game_time = eval(new_line)
        if results_key in line:
            current_game_tuple = eval( line.partition(results_key)[2] )
        if master_key in line:
            all_game_trials += 1
#            this_game_results = eval( line.partition(key)[2] )
            all_game_time += this_game_time
            sum_game_results = list_add( sum_game_results, current_game_tuple )
            all_game_results[ get_index( current_game_tuple ) ] += 1
#            current_game_tuple = this_game_results[0]
#            for i in range(NUM_PLAYERS):
#                this_player_score = current_game_tuple[ i ]
#            last_index = NUM_PLAYERS
#            #I keep the type of score (win, tie, loss)
#                if this_score == 0:
#                    all_game_results[ i ][last_index] = all_game_results[ i ][last_index] + 1
#                else:
#                    inverse = int( float(NUM_PLAYERS)/this_player_score )
#                    all_game_results[i][ inverse - 1 ] = all_game_results[i][ inverse - 1 ] + 1
    all_game_results = tuple( all_game_results )
    if all_game_trials > 0:
        current_confidence = decibels( c_bayesian.main(game_results = all_game_results, trials = trials ) )
        trials_used = trials
        if abs( current_confidence ) < 40: #If there is at least a one in ten thousand chance,
            current_confidence = decibels( c_bayesian.main(game_results = all_game_results, trials = 100 * trials ) )
            trials_used = 100 * trials
            #run more trials to be safe
#        current_confidence = decibels( main(game_results = all_game_results, trials = trials ) )
#    comparisons[ (a,b) ] = (current_confidence, all_game_trials, all_game_time, sum_game_results ) 
    f = open("Results/bayesian.log","a")
    f.write( time.asctime() + ": " + to_write_confidence + str(current_confidence) + "\n" )
    f.write( time.asctime() + ": " + to_write_time + str(all_game_time) + "\n" )
    f.write( time.asctime() + ": " + to_write_trials + str(all_game_trials) + "\n" )
    f.write( time.asctime() + ": " + to_write_sum + str(sum_game_results) + "\n" )
    f.write( time.asctime() + ": The bayesian algorithm used " + str(trials_used) + " trials.\n") 
    f.close()
    return (current_confidence, all_game_trials, all_game_time, sum_game_results, all_game_results, trials_used ) 
def get_results(comparisons):
    import time, random, math
    name = "Results/Readable/Bayesian_Readable_"+ time.asctime() + " " + str(random.randrange(10**9) )+ ".txt"
    name = name.replace(" ","_")
    f = open(name, "a")
#    print len(comparisons)
    results_list = []
    for c in comparisons.keys():
        fixed, invader = c
        title = "Fixed: " + str(fixed) + " Invader: " + str(invader) + "\n"
        f.write(title)
        f.write( "Current Confidence: " + str(comparisons[c][0]) + "\n" )
        num_trials = comparisons[c][1]
        f.write( "Number of trials: " + str(comparisons[c][1]) + "\n" )
        f.write( "Amount of time spent: " + str(comparisons[c][2]) + "\n" )
        invader_score = comparisons[c][3][-1]
        f.write( "Summed results of games: " + str(comparisons[c][3]) + "\n\n" )
        confidence = comparisons[c][0]
        results_list.append( [ title, num_trials, invader_score, fixed, invader, confidence ] )
    f.close()
    results_list.sort()
    name = "Results/Readable/Bayesian_Analysis_by_Fixed_"+ time.asctime() + " " + str(random.randrange(10**9) )+ ".txt"
    name = name.replace(" ","_")
    g_name = "Results/Readable/Bayesian_Summary_"+ time.asctime() + " " + str(random.randrange(10**9) )+ ".txt"
    g_name = g_name.replace(" ","_")
    g = open(g_name, "a")
    f = open(name, "a")
    previously_fixed = None
    fixed_wins = 0
    fixed_ties = 0
    fixed_losses = 0
    total_number_trials = 0
    first = True
    for x in results_list:
        title = x[0]
        num_trials = x[1]
        invader_score = x[2]
        fixed = x[3]
        confidence = x[5]
        if fixed != previously_fixed:
            if not first:
                g.write("Results where " + str(previously_fixed) + " is fixed:\n")
                g.write("Was ES against this many strategies: " + str(fixed_wins) + "\n")
                g.write("Was in a statistical tie with this many strategies: " + str(fixed_ties) + "\n")
                g.write("Was not ES against this many strategies: " + str(fixed_losses) + "\n")
                g.write("Net score: " + str(fixed_wins - fixed_losses) + "\n\n")
                fixed_wins = 0
                fixed_ties = 0
                fixed_losses = 0
            previously_fixed = fixed
        first = False
        f.write(title)
        f.write("Number of trials: " + str(num_trials) + "\n" )
        total_number_trials += num_trials
        f.write("Invader's score: " + str(invader_score) + "\n" )
        ratio = float(invader_score) / num_trials
        f.write("Ratio: " + str(ratio) + "\n" )
        tie = False
        if ratio < 1:
            f.write("The fixed player IS evolutionarily stable against the invader." + "\n" )
            seems_like_win = True
        elif ratio > 1:
            f.write("The fixed player is NOT evolutionarily stable against the invader." + "\n" )
            seems_like_win = False
        else:
           f.write("Unable to make a decision.\n")
           tie = True
        uncertainty = NUM_PLAYERS * math.sqrt( num_trials )
        lower_bound = invader_score - uncertainty
        upper_bound = invader_score + uncertainty
        f.write("Lower bound on invader's score: " + str(lower_bound) + "\n" )
        f.write("Upper bound on invader's score: " + str(upper_bound) + "\n" )
        if num_trials >= lower_bound and num_trials <= upper_bound:
           f.write("It is POSSIBLE that this result is incorrect.\n" )
           fixed_ties += 1
        elif tie:
            fixed_ties += 1
        elif seems_like_win:
            fixed_wins += 1
        else:
            fixed_losses += 1
        f.write("Here's the confidence: " + str(confidence) + "\n") 
        f.write("\n")
    if not first:
        g.write("Results where " + str(previously_fixed) + " is fixed:\n")
        g.write("Was ES against this many strategies: " + str(fixed_wins) + "\n")
        g.write("Was in a statistical tie with this many strategies: " + str(fixed_ties) + "\n")
        g.write("Was not ES against this many strategies: " + str(fixed_losses) + "\n")
        g.write("Net score: " + str(fixed_wins - fixed_losses) + "\n\n")
    f.close()
    results_list.sort(key = lambda x: str(x[4]))
    name = "Results/Readable/Bayesian_Analysis_by_Invader_"+ time.asctime() + " " + str(random.randrange(10**9) )+ ".txt"
    name = name.replace(" ","_")
    f = open(name, "a")
    previously_invading = None
    invader_wins = 0
    invader_ties = 0
    invader_losses = 0
    first = True
    for x in results_list:
        title = x[0]
        num_trials = x[1]
        invader_score = x[2]
        invader = x[4]
        confidence = x[5]
        if invader != previously_invading:
            if not first:
                g.write("Results where " + str(previously_invading) + " is invader:\n")
                g.write("Could invade this many strategies: " + str(invader_wins) + "\n")
                g.write("Was in a statistical tie with this many strategies: " + str(invader_ties) + "\n")
                g.write("Could not invade this many strategies: " + str(invader_losses) + "\n")
                g.write("Net score: " + str(invader_wins - invader_losses) + "\n\n")
                invader_wins = 0
                invader_ties = 0
                invader_losses = 0
            previously_invading = invader
        first = False
        f.write(title)
        f.write("Number of trials: " + str(num_trials) + "\n" )
        f.write("Invader's score: " + str(invader_score) + "\n" )
        ratio = float(invader_score) / num_trials
        f.write("Ratio: " + str(ratio) + "\n" )
        if ratio < 1:
            f.write("The fixed player IS evolutionarily stable against the invader." + "\n" )
            seems_like_win = False
        elif ratio > 1:
            f.write("The fixed player is NOT evolutionarily stable against the invader." + "\n" )
            seems_like_win = True
        else:
            f.write("Unable to make a decision.\n")
            tie = True
        uncertainty = NUM_PLAYERS * math.sqrt( num_trials )
        lower_bound = invader_score - uncertainty
        upper_bound = invader_score + uncertainty
        f.write("Lower bound on invader's score: " + str(lower_bound) + "\n" )
        f.write("Upper bound on invader's score: " + str(upper_bound) + "\n" )
        if num_trials >= lower_bound and num_trials <= upper_bound:
            f.write("It is POSSIBLE that this result is incorrect.\n" )
            invader_ties += 1
        elif tie:
            invader_ties += 1
        elif seems_like_win:
            invader_wins += 1
        else:
            invader_losses += 1
        f.write("Here's the confidence: " + str(confidence) + "\n") 
        f.write("\n")
    if not first:
        g.write("Results where " + str(previously_invading) + " is invader:\n")
        g.write("Could invade this many strategies: " + str(invader_wins) + "\n")
        g.write("Was in a statistical tie with this many strategies: " + str(invader_ties) + "\n")
        g.write("Could not invade this many strategies: " + str(invader_losses) + "\n")
        g.write("Net score: " + str(invader_wins - invader_losses) + "\n\n")
    g.write("\n\n" + "The total number of trials for all comparisons is " + str(total_number_trials) )
    f.close()
    g.close()
def is_significant(comparison):
    import math
    num_trials = comparison[1]
    invader_score = comparison[3][-1]
    uncertainty = NUM_PLAYERS * math.sqrt( num_trials )
    lower_bound = invader_score - uncertainty
    upper_bound = invader_score + uncertainty
    return num_trials < lower_bound or num_trials > upper_bound
def list_add( a, b):
    c = []
    if len(a) != len(b):
        raise Exception( str(len(a)) + " != " + str(len(b)) )
    for i in range(len(a)):
        c.append( a[i] + b[i] )
    return c
def get_index( result_tuple):
    '''Takes a tuple like (2.5, 0, 2.5, 0, 0) and makes it into
    (1,0,1,0,0), then converts the base two number 10100 into
    base ten -- 20.'''
    new = []
    for x in result_tuple:
        if x == 0:
            new.append(0)
        else:
            new.append(1)
    new.reverse()
    coeff = 1
    total = 0
    for x in new:
        total += x * coeff
        coeff *= 2
    return total
class Wrapper:
    '''Takes an algorithm from inspect and has a nice interface'''
    def __init__(self, input_tuple):
        self.__tuple = input_tuple
        self.__name = self.__tuple[0]
        self.__function = self.__tuple[1]
    def get_name(self):
        return self.__name
    def get_function(self):
        return self.__function
    def get_tuple(self):
        return self.__tuple
    def __repr__(self):
        return "Wrapper(" + repr(self.get_tuple()) + ")"
    def __str__(self):
        return self.get_name()
    def __neq__(self, other):
        return not self == other
    def __eq__(self, other):
        return self.get_tuple() == other.get_tuple()
    def __hash__(self):
        return hash(self.get_tuple())
def decibels(x):
    x = Decimal(x)
    if x < 0.5:
        odds = x/(1-x)
        return 10 * odds.log10()
    else:
        odds = (1-x)/x
        return -10 * odds.log10()
