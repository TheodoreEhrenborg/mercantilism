def main():
    #import Monte Carlo algorithm
    from skmonaco import mcquad
    #integrate all probabilities over the hypercube
    #integrate all above_average (or below average) over the hypercube
    #Divide to get the chance that 1 is not ES against 2
def all_cases( point_tuple, game_results):
    '''Default: assume game_results is sorted as wins, 2-ties, ..., n-ties,
    lose. Wins refer to the invading player's wins'''
    point = list( point_tuple )
    point.sort()
    point = (0,) + point + (1,)
    density = 1.0
    for n in range( len(game_results) ):
        how_many_games = game_results[n]
        interval = point[n+1] - point[n]
        density *= interval ** how_many_games
    return density
def below_average( point_tuple, game_results):
    '''Since the average score decreases compared to the total as n increases,
    most of the volume of the cube
    consists of events where the invading strategy is above average
    (I hope). Thus to save time we should only calculate in places
    where the invader's score is below average. '''
