#cython: nonecheck=True
class SuperFloat:
    def __init__(self, f, exp = 0):
        import math
        if f == 0:
            self.__value = 0
            self.__exp = 0
        else:
            self.__exp = int( math.log( abs(f), 10 ) )
            self.__value = f * 10 ** -self.__exp
            self.__exp += exp
            #Here we should use format(2**320, "E").partition("E+") to get the 
            #exp and value without multiplying by large numbers
    def get_exp(self):
        return self.__exp
    def get_value(self):
        return self.__value
    def __add__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        if self.get_exp() > other.get_exp():
            other_float = other.get_value() * 10 **(other.get_exp() - self.get_exp())
            return SuperFloat( self.get_value() + other_float, self.get_exp())
        else:
            self_float = self.get_value() * 10 ** (self.get_exp() - other.get_exp())
            return SuperFloat( other.get_value() + self_float, other.get_exp())
    def __sub__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        return self + SuperFloat( -1 * other.get_value(), other.get_exp())
    def __mul__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        return SuperFloat( self.get_value() * other.get_value(), self.get_exp() + other.get_exp())
    def __div__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        return SuperFloat( self.get_value() / other.get_value(), self.get_exp() - other.get_exp())
    def old_pow(self,other):
        if not isinstance(other, int) or other < 0:
            raise Exception("Other is not a nonnegative integer")
        start = SuperFloat( 1 )
        for x in range( other ):
            start *= self
        return start
    def __pow__(self,other):
        if not isinstance(other, int) or other < 0:
            raise Exception("Other is not a nonnegative integer")
        start = SuperFloat( 1 )
        current_square = self
        in_base_2 = to_base_2(other)
        in_base_2.reverse()
        for x in in_base_2:
            if x:
                start *= current_square
            current_square = current_square * current_square 
        return start
    def as_float(self):
        return float(self.get_value() * 10 ** self.get_exp())
    def __cmp__(self, other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        x = self - other
        if x.get_value() == 0:
            return 0
        elif x.get_value() > 0:
            return 1
        else:
            return -1
    def __repr__(self):
        return "SuperFloat(" + str( self.get_value()) +str(" , ") + str( self.get_exp() ) + str(")")
def main(game_results, trials = 1e5, default_cushion = None):
    '''Uses five dimensions with multiplicities and the Decimal class'''
    #Note that game_results is of the form ( x , y , ... , w )
    #where each value is the number of times a game has had a certain outcome (like the first and third players tie)
    #However, the first element of game_results is zero because all players cannot all lose
    #import Monte Carlo integration algorithm from scikit-monaco library
    import time, math
    from skmonaco import mcquad, mcmiser
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Got game_results = " + str(game_results) + 
            " Got trials = " + str(trials) + "\n")
    f.close()
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
        c = count(base_2)
        if base_2[-1] == 0:
            compressed[0] += game_results[i]
            multiplicities[0] += 1
            weights[0] = 0 #Note that losses come first, then wins, 2-ties, ..., n-ties
        else:
            compressed[c] += game_results[i]
            multiplicities[c] += 1
            weights[c] =  float(n)/c
#    print compressed, weights, multiplicities
    #Now I need to run below_average_cases. I should figure out the 
    #weights of each outcome -- a win is n points -- and the average 
    #utility points to beat. I'll do that here instead of in the 
    #thousands of runs of below_average_cases.
    average = 1
    abridged = game_results[1:]
    #integrate all probabilities over the hypercube
    #For n players, a game could end in 2^n - 1 ways
#    cushion = Decimal(1)
    best_point_tuple = tuple( normalize( compressed ) )
    result, error = both( point_tuple = best_point_tuple, compressed, weights,
                         average, multiplicities, cushion = Decimal(1) )
    cushion = result[0]
#    if default_cushion == None:
#        cushion = sample5(compressed, multiplicities,n, trials/10)
#    else:
#        cushion = Decimal(default_cushion)
    result, error = mcquad( both , args = [compressed, weights, average, multiplicities, cushion ],
                            npoints = trials, xl = zeros(n), xu = ones(n) )
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Calculated total probability = " + str(result[0]) + ", error = " +
            str(error[0]) + "\n")
    f.write(time.asctime() + ": Calculated below average probability = " + str(result[1]) + ", error = " +
            str(error[1]) + "\n")
    f.close()
    #Divide to get the chance that 1 is not ES against 2
    return (result[1] / result[0], cushion)
def both( point_tuple, compressed_game_results, weights, average, multiplicities, cushion):
    point = list( point_tuple )
    point.sort()
    point = [0] + point + [1,]
    density = Decimal(1)
#    average_multiplier = 0
    for i in range( len(compressed_game_results) ):
        how_many_games = compressed_game_results[i]
        m = multiplicities[i]
        interval = Decimal( point[i+1] - point[i] )
#        average_multiplier += interval * m
        density *= interval ** how_many_games
        density *= interval ** (m-1)
#        density *= m ** interval
#    density *= average_multiplier
    result1 = float(density / cushion)
    expected_utility = 0
    for i in range( len(weights) ):
        expected_utility += weights[i] *  ( point[i+1] - point[i] )
    if expected_utility < average:
        result2 = result1
    elif expected_utility > average:
        result2 = 0
    else:
        result2 = 0.5 * result1
    return np.array( [result1,result2] ) 
def sample5( compressed_game_results, multiplicities, n, trials = 1e2):
    '''Returns a Decimal indicating the highest density found'''
    import random
    counter = 0
    current_max = Decimal(0)
    while counter < trials:
        counter+=1
#        print counter
        point = []
        for x in range( n ):
            point.append( random.random() )
        point.sort()
        point = [0] + point + [1,]
        density = Decimal(1.0)
        for i in range( len(compressed_game_results) ):
            how_many_games = compressed_game_results[i]
            m = multiplicities[i]
            interval = Decimal( point[i+1] - point[i] )
#        average_multiplier += interval * m
            density *= interval ** how_many_games
            density *= interval ** (m-1)
#        density *= m ** interval
#    density *= average_multiplier
        current_max = max( current_max, density)
    return current_max
def list_total( l ):
    t = 0
    for x in l:
        t += x
    return t
def normalize( l ):
    t = list_total( l )
    new = []
    for x in l:
        new.append( float(x) / t )
    return new
