'''Calculates the probability/significance'''
def main(game_results, trials = 1e5):
    #import Monte Carlo integration algorithm from scikit-monaco library
    import time
    from skmonaco import mcquad
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Got game_results = " + str(game_results) + 
            " Got trials = " + str(trials) + "\n")
    f.close()
    #n is the number of players
    n = len( game_results ) - 1
    #integrate all probabilities over the hypercube
    all_results = mcquad( all_cases , args = [game_results],
                            npoints=trials, xl = zeros(n), xu = ones(n) )
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Calculated all_results = " + str(all_results) + "\n")
    f.close()
    #Now I need to run below_average_cases. I should figure out the 
    #weights of each outcome -- a win is n points -- and the average 
    #utility points to beat. I'll do that here instead of in the 
    #thousands of runs of below_average_cases.
    weights = []
    for i in range(1,n+1):
        weights.append( float(n)/i )
    weights.append( 0 )
    average = 1
    #integrate all below average over the hypercube
    below_average_results = mcquad( below_average_cases , args = [game_results, weights, average],
                            npoints=trials, xl = zeros(n), xu = ones(n) )
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Calculated below_average_results = " + 
            str(below_average_results) + "\n")
    f.close()
    #Divide to get the chance that 1 is not ES against 2
    return below_average_results[0] / all_results[0]
def zeros(n):
    result = []
    for i in range(n):
        result.append(0.0)
    return result
def ones(n):
    result = []
    for i in range(n):
        result.append(1.0)
    return result
def all_cases( point_tuple, game_results):
    '''Default: assume game_results is sorted as wins, 2-ties, ..., n-ties,
    losses. Wins refer to the invading player's wins'''
    #Is the next line a waste of time?
    if len( point_tuple ) != len(game_results) - 1:
        raise Exception("len(point_tuple) = " + str(len(point_tuple)) 
            + ", len(game_results) = " + str(len(game_results)) )
    point = list( point_tuple )
    point.sort()
    point = [0,] + point + [1,]
    density = 1.0
    for i in range( len(game_results) ):
        how_many_games = game_results[i]
        interval = point[i+1] - point[i]
        density *= interval ** how_many_games
    return density
def below_average_cases( point_tuple, game_results, weights, average):
    '''Since the average score decreases compared to the total as n increases,
    most of the volume of the cube
    consists of events where the invading strategy is above average
    (I hope). Thus to save time we should only calculate in places
    where the invader's score is below average. '''
    point = list( point_tuple )
    point.sort()
    point = [0,] + point + [1,]
    expected_utility = 0
    for i in range( len(weights) ):
        expected_utility += weights[i] *  ( point[i+1] - point[i] )
    if expected_utility < average:
        return all_cases( point_tuple, game_results )
    else:
        return 0
